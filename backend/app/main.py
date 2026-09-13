from io import BytesIO

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware

from PIL import Image

from .model_service import ppe_model
from .reasoning import (
    answer_query,
    safety_analysis,
    confidence_level
)


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Construction PPE Safety Intelligence API",
    description=(
        "RT-DETR based construction-site PPE detection "
        "and rule-based safety reasoning API."
    ),
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def root():

    return {
        "status": "running",
        "service": "Construction PPE Safety Intelligence API",
        "model": "RT-DETR"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_loaded": True
    }


# =========================================================
# IMAGE LOADING
# =========================================================

async def load_image(
    file: UploadFile
):

    if not file.content_type:

        raise HTTPException(
            status_code=400,
            detail="File type could not be determined."
        )

    if not file.content_type.startswith("image/"):

        raise HTTPException(
            status_code=400,
            detail="Only image files are supported."
        )

    contents = await file.read()

    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:

        image = Image.open(
            BytesIO(contents)
        ).convert("RGB")

        return image

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid image file."
        )


# =========================================================
# DETECT
# =========================================================

@app.post("/detect")
async def detect(
    file: UploadFile = File(...)
):

    image = await load_image(file)

    detections = ppe_model.predict(image)

    return {
        "success": True,
        "model": "RT-DETR",
        "image_width": image.width,
        "image_height": image.height,
        "detection_count": len(detections),
        "detections": [
            detection.model_dump()
            for detection in detections
        ]
    }


# =========================================================
# REASON
# =========================================================

@app.post("/reason")
async def reason(
    query: str,
    file: UploadFile = File(...)
):

    image = await load_image(file)

    detections = ppe_model.predict(image)

    intent, answer, safety_status = answer_query(
        query,
        detections
    )

    analysis = safety_analysis(
        detections
    )

    confidence = confidence_level(
        detections
    )

    return {
        "success": True,
        "query": query,
        "intent": intent,
        "answer": answer,
        "safety_status": safety_status,
        "confidence": confidence,
        "evidence": analysis,
        "detections": [
            detection.model_dump()
            for detection in detections
        ]
    }


# =========================================================
# SAFETY REPORT
# =========================================================

@app.post("/safety-report")
async def safety_report(
    file: UploadFile = File(...)
):

    image = await load_image(file)

    detections = ppe_model.predict(image)

    analysis = safety_analysis(
        detections
    )

    confidence = confidence_level(
        detections
    )

    return {
        "success": True,
        "safety_status": analysis["status"],
        "confidence": confidence,
        "evidence": analysis,
        "detection_count": len(detections)
    }