import os
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
from ultralytics import RTDETR

from .schemas import Detection, BoundingBox


load_dotenv()


MODEL_PATH = os.getenv("MODEL_PATH", "models/best.pt")
CONFIDENCE_THRESHOLD = float(
    os.getenv("CONFIDENCE_THRESHOLD", "0.35")
)
IMAGE_SIZE = int(
    os.getenv("IMAGE_SIZE", "640")
)
DEVICE = os.getenv("DEVICE", "0")


class PPEModel:

    def __init__(self):

        model_path = Path(MODEL_PATH)

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {model_path.resolve()}"
            )

        print("=" * 60)
        print("Loading PPE Detection Model")
        print("=" * 60)
        print(f"Model path : {model_path.resolve()}")
        print(f"Confidence : {CONFIDENCE_THRESHOLD}")
        print(f"Image size : {IMAGE_SIZE}")
        print(f"Device     : {DEVICE}")

        self.model = RTDETR(str(model_path))

        print("Model loaded successfully.")
        print("=" * 60)

    def predict(self, image: Image.Image):

        results = self.model.predict(
            source=image,
            imgsz=IMAGE_SIZE,
            conf=CONFIDENCE_THRESHOLD,
            device=DEVICE,
            verbose=False
        )

        result = results[0]

        detections = []

        if result.boxes is None:
            return detections

        boxes = result.boxes

        for i in range(len(boxes)):

            xyxy = boxes.xyxy[i].tolist()

            confidence = float(
                boxes.conf[i].item()
            )

            class_id = int(
                boxes.cls[i].item()
            )

            class_name = self.model.names[class_id]

            detection = Detection(
                class_id=class_id,
                class_name=class_name,
                confidence=round(confidence, 4),
                bbox=BoundingBox(
                    x1=round(xyxy[0], 2),
                    y1=round(xyxy[1], 2),
                    x2=round(xyxy[2], 2),
                    y2=round(xyxy[3], 2)
                )
            )

            detections.append(detection)

        return detections


# Load ONCE when the server starts
ppe_model = PPEModel()