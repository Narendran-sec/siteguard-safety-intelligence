from ultralytics import YOLO
from pathlib import Path

MODEL_PATH = "models/v2best.pt"
IMAGE_PATH = "test image.jpg"

print("Loading V2 model...")
model = YOLO(MODEL_PATH)

print("Model loaded successfully.")
print("Running inference...\n")

results = model.predict(
    source=IMAGE_PATH,
    conf=0.30,
    save=True,
    verbose=True
)

print("\n" + "=" * 50)
print("DETECTIONS")
print("=" * 50)

for result in results:
    if result.boxes is None:
        print("No detections.")
        continue

    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = model.names[class_id]

        print(f"{class_name:<15} {confidence:.3f}")

print("\nTest completed.")