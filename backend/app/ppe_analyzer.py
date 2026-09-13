from pathlib import Path

import torch
from ultralytics import YOLO


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "v2best.pt"

CONFIDENCE_THRESHOLD = 0.30
DECISION_MARGIN = 0.10

# Render-friendly inference settings
IMAGE_SIZE = 320
MAX_DETECTIONS = 50


# ============================================================
# CPU CONFIGURATION
# ============================================================

# Keep CPU usage predictable on small cloud instances.
torch.set_num_threads(1)


# ============================================================
# V2 MODEL PPE CLASSES
# ============================================================

PPE_PAIRS = {
    "helmet": ("helmet", "no_helmet"),
    "gloves": ("gloves", "no_gloves"),
    "vest": ("vest", None),
    "boots": ("boots", "no_boots"),
    "goggles": ("goggles", "no_goggle"),
}


# ============================================================
# LOAD MODEL
# ============================================================

print("========================================")
print("Loading V2 PPE model...")
print(f"Model path: {MODEL_PATH}")
print("========================================")

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model not found at: {MODEL_PATH}"
    )

model = YOLO(str(MODEL_PATH))

print("V2 model loaded successfully.")
print("Classes:")

for class_id, class_name in model.names.items():
    print(f"{class_id} -> {class_name}")

print("Inference device: CPU")
print(f"Inference image size: {IMAGE_SIZE}")
print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
print("========================================")


# ============================================================
# PPE ANALYZER
# ============================================================

def analyze_ppe(image_path):

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    print("----------------------------------------")
    print(f"Starting PPE analysis: {image_path.name}")
    print("Starting YOLO inference...")
    print("----------------------------------------")

    # ========================================================
    # RUN INFERENCE
    # ========================================================

    results = model.predict(
        source=str(image_path),

        # Render-friendly settings
        imgsz=IMAGE_SIZE,
        device="cpu",
        workers=0,

        # Detection settings
        conf=CONFIDENCE_THRESHOLD,
        max_det=MAX_DETECTIONS,

        # Keep output quiet
        verbose=False
    )

    print("YOLO inference completed successfully.")

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
    # COLLECT DETECTIONS
    # ========================================================

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            class_name = model.names[class_id]

            print(
                f"Detection: {class_name} "
                f"(confidence={confidence:.3f})"
            )

            # ------------------------------------------------
            # PERSON
            # ------------------------------------------------

            if class_name == "Person":
                person_detected = True

            # ------------------------------------------------
            # PPE
            # ------------------------------------------------

            for ppe, (positive_class, negative_class) in PPE_PAIRS.items():

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

    # ========================================================
    # DETERMINE PPE STATUS
    # ========================================================

    ppe_results = {}

    for ppe in PPE_PAIRS:

        positive = positive_scores[ppe]
        negative = negative_scores[ppe]

        # ----------------------------------------------------
        # POSITIVE DETECTION
        # ----------------------------------------------------

        if positive >= CONFIDENCE_THRESHOLD:

            if (
                negative >= CONFIDENCE_THRESHOLD
                and negative > positive + DECISION_MARGIN
            ):
                status = "missing"
            else:
                status = "present"

        # ----------------------------------------------------
        # NEGATIVE DETECTION
        # ----------------------------------------------------

        elif negative >= CONFIDENCE_THRESHOLD:

            status = "missing"

        # ----------------------------------------------------
        # NO RELIABLE EVIDENCE
        # ----------------------------------------------------

        else:

            status = "uncertain"

        ppe_results[ppe] = {
            "status": status,
            "positive_confidence": round(positive, 3),
            "negative_confidence": round(negative, 3)
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
    print(f"Analysis complete: {overall_status}")
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