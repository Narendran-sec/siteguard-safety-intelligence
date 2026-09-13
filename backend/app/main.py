from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid

from .ppe_analyzer import analyze_ppe


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="PPE Detection API",
    description="Construction Site PPE Compliance Detection API",
    version="1.0.0"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        # Your deployed frontend URL will be added here
        # after we deploy the frontend.
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "PPE Detection API is running",
        "status": "online"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# ANALYZE IMAGE
# ============================================================

@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...)
):
    print("========== ANALYZE REQUEST RECEIVED ==========")

    extension = Path(file.filename or "").suffix.lower()

    if not extension:
        extension = ".jpg"

    filename = f"{uuid.uuid4()}{extension}"
    image_path = UPLOAD_DIR / filename

    try:
        # Save image
        contents = await file.read()

        with open(image_path, "wb") as buffer:
            buffer.write(contents)

        print(f"Image saved: {image_path}")
        print(f"Image size: {len(contents)} bytes")

        # Run YOLO
        print("========== STARTING YOLO ==========")

        result = analyze_ppe(str(image_path))

        print("========== YOLO COMPLETED ==========")
        print(f"Result: {result}")

        return JSONResponse(content=result)

    except Exception as e:

        print("========== PPE ANALYSIS ERROR ==========")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {str(e)}")
        print("========================================")

        raise HTTPException(
            status_code=500,
            detail=f"PPE analysis failed: {str(e)}"
        )

    finally:

        if image_path.exists():
            try:
                image_path.unlink()
                print("Temporary image deleted.")
            except Exception as cleanup_error:
                print(f"Cleanup error: {cleanup_error}")