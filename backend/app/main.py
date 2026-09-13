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
    print(f"Filename: {file.filename}")
    print(f"Content type: {file.content_type}")

    try:
        contents = await file.read()

        print(f"File received successfully")
        print(f"File size: {len(contents)} bytes")

        return {
            "status": "upload_received",
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(contents)
        }

    except Exception as e:
        print("========== UPLOAD ERROR ==========")
        print(str(e))
        print("===================================")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )