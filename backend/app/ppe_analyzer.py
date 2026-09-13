from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort
import requests


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "v2best.onnx"

# Public Hugging Face model
MODEL_URL = (
    "https://huggingface.co/"
    "NarendranKumar/siteguard-rtdetr/"
    "resolve/main/v2best.onnx"
)

IMAGE_SIZE = 320
CONFIDENCE_THRESHOLD = 0.30
DECISION_MARGIN = 0.10
MAX_DETECTIONS = 50


# ============================================================
# CLASS NAMES
# ============================================================

CLASS_NAMES = {
    0: "helmet",
    1: "gloves",
    2: "vest",
    3: "boots",
    4: "goggles",
    5: "none",
    6: "Person",
    7: "no_helmet",
    8: "no_goggle",
    9: "no_gloves",
    10: "no_boots",
}


# ============================================================
# PPE PAIRS
# ============================================================

PPE_PAIRS = {
    "helmet": ("helmet", "no_helmet"),
    "gloves": ("gloves", "no_gloves"),
    "vest": ("vest", None),
    "boots": ("boots", "no_boots"),
    "goggles": ("goggles", "no_goggle"),
}


# ============================================================
# DOWNLOAD MODEL IF NEEDED
# ============================================================

def ensure_model():

    if MODEL_PATH.exists():

        print("========================================")
        print("RT-DETR ONNX model already exists.")
        print(f"Model path: {MODEL_PATH}")
        print("========================================")

        return

    print("========================================")
    print("RT-DETR ONNX model not found locally.")
    print("Downloading model from Hugging Face...")
    print(f"URL: {MODEL_URL}")
    print("========================================")

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Temporary file prevents a partially downloaded model
    # from being used if the download fails.
    temp_path = MODEL_DIR / "v2best.onnx.download"

    try:

        with requests.get(
            MODEL_URL,
            stream=True,
            timeout=600
        ) as response:

            response.raise_for_status()

            total_size = int(
                response.headers.get(
                    "content-length",
                    0
                )
            )

            downloaded = 0

            with open(
                temp_path,
                "wb"
            ) as file:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):

                    if not chunk:
                        continue

                    file.write(chunk)

                    downloaded += len(chunk)

                    if total_size:

                        percent = (
                            downloaded /
                            total_size
                        ) * 100

                        print(
                            f"\rDownloading: "
                            f"{percent:.1f}% "
                            f"({downloaded / 1024 / 1024:.1f} MB / "
                            f"{total_size / 1024 / 1024:.1f} MB)",
                            end=""
                        )

        print()

        temp_path.replace(
            MODEL_PATH
        )

        print("RT-DETR ONNX model downloaded successfully.")
        print(f"Saved to: {MODEL_PATH}")

    except Exception:

        if temp_path.exists():
            temp_path.unlink()

        raise


# ============================================================
# ENSURE MODEL
# ============================================================

ensure_model()


# ============================================================
# LOAD ONNX MODEL
# ============================================================

print("========================================")
print("Loading RT-DETR ONNX model...")
print(f"Model path: {MODEL_PATH}")
print("========================================")


# Keep ONNX Runtime memory usage controlled.
session_options = ort.SessionOptions()

session_options.intra_op_num_threads = 1
session_options.inter_op_num_threads = 1

session_options.graph_optimization_level = (
    ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
)


session = ort.InferenceSession(
    str(MODEL_PATH),
    sess_options=session_options,
    providers=[
        "CPUExecutionProvider"
    ]
)


INPUT_NAME = session.get_inputs()[0].name
OUTPUT_NAME = session.get_outputs()[0].name


print("RT-DETR ONNX model loaded successfully.")
print(f"Input name: {INPUT_NAME}")
print(
    f"Input shape: "
    f"{session.get_inputs()[0].shape}"
)
print(f"Output name: {OUTPUT_NAME}")
print(
    f"Output shape: "
    f"{session.get_outputs()[0].shape}"
)
print("Inference device: CPU")
print(f"Image size: {IMAGE_SIZE}")
print(
    f"Confidence threshold: "
    f"{CONFIDENCE_THRESHOLD}"
)
print("========================================")


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image_path: Path):

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        raise ValueError(
            f"Could not read image: {image_path}"
        )

    # OpenCV loads BGR.
    # Model expects RGB.
    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    image = cv2.resize(
        image,
        (
            IMAGE_SIZE,
            IMAGE_SIZE
        ),
        interpolation=cv2.INTER_LINEAR
    )

    image = (
        image.astype(
            np.float32
        ) / 255.0
    )

    # HWC -> CHW
    image = np.transpose(
        image,
        (2, 0, 1)
    )

    # Add batch dimension
    image = np.expand_dims(
        image,
        axis=0
    )

    return np.ascontiguousarray(
        image
    )


# ============================================================
# PPE ANALYZER
# ============================================================

def analyze_ppe(image_path):

    image_path = Path(
        image_path
    )

    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    print("----------------------------------------")
    print(
        f"Starting PPE analysis: "
        f"{image_path.name}"
    )
    print(
        "Starting RT-DETR ONNX inference..."
    )
    print("----------------------------------------")

    # ========================================================
    # PREPROCESS
    # ========================================================

    input_tensor = preprocess_image(
        image_path
    )

    # ========================================================
    # INFERENCE
    # ========================================================

    outputs = session.run(
        [OUTPUT_NAME],
        {
            INPUT_NAME: input_tensor
        }
    )

    detections = outputs[0][0]

    print(
        f"RT-DETR inference completed. "
        f"Raw detections: {len(detections)}"
    )

    # ========================================================
    # SCORE STORAGE
    # ========================================================

    positive_scores = {
        ppe: 0.0
        for ppe in PPE_PAIRS
    }

    negative_scores = {
        ppe: 0.0
        for ppe in PPE_PAIRS
    }

    person_detected = False

    # ========================================================
    # PROCESS DETECTIONS
    # ========================================================

    detection_count = 0

    for detection in detections:

        if len(detection) != 6:
            continue

        confidence = float(
            detection[4]
        )

        class_id = int(
            detection[5]
        )

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        class_name = CLASS_NAMES.get(
            class_id
        )

        if class_name is None:
            continue

        detection_count += 1

        print(
            f"Detection: {class_name} "
            f"(confidence={confidence:.3f})"
        )

        # ----------------------------------------------------
        # PERSON
        # ----------------------------------------------------

        if class_name == "Person":

            person_detected = True

        # ----------------------------------------------------
        # PPE
        # ----------------------------------------------------

        for ppe, (
            positive_class,
            negative_class
        ) in PPE_PAIRS.items():

            if class_name == positive_class:

                positive_scores[ppe] = max(
                    positive_scores[ppe],
                    confidence
                )

            elif (
                negative_class is not None
                and class_name == negative_class
            ):

                negative_scores[ppe] = max(
                    negative_scores[ppe],
                    confidence
                )

    print(
        f"Usable detections: "
        f"{detection_count}"
    )

    # ========================================================
    # DETERMINE PPE STATUS
    # ========================================================

    ppe_results = {}

    for ppe in PPE_PAIRS:

        positive = positive_scores[ppe]
        negative = negative_scores[ppe]

        if positive >= CONFIDENCE_THRESHOLD:

            if (
                negative >= CONFIDENCE_THRESHOLD
                and
                negative >
                positive + DECISION_MARGIN
            ):

                status = "missing"

            else:

                status = "present"

        elif negative >= CONFIDENCE_THRESHOLD:

            status = "missing"

        else:

            status = "uncertain"

        ppe_results[ppe] = {
            "status": status,
            "positive_confidence": round(
                positive,
                3
            ),
            "negative_confidence": round(
                negative,
                3
            )
        }

    # ========================================================
    # OVERALL STATUS
    # ========================================================

    missing = [
        ppe
        for ppe, result in ppe_results.items()
        if result["status"] == "missing"
    ]

    uncertain = [
        ppe
        for ppe, result in ppe_results.items()
        if result["status"] == "uncertain"
    ]

    if not person_detected:

        overall_status = "no_person"

    elif missing:

        overall_status = "violation"

    elif uncertain:

        overall_status = "uncertain"

    else:

        overall_status = "compliant"

    print("----------------------------------------")
    print(
        f"Analysis complete: "
        f"{overall_status}"
    )
    print("----------------------------------------")

    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {
        "image": image_path.name,
        "person_detected": person_detected,
        "status": overall_status,
        "ppe": ppe_results,
        "missing": missing,
        "uncertain": uncertain
    }