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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
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
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "PPE Detection API is running",
        "status": "online"
    }


# ============================================================
# HEALTH
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

    # --------------------------------------------------------
    # ALLOWED FILE TYPES
    # --------------------------------------------------------

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/jpg",
        "image/webp"
    }

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are supported."
        )

    # --------------------------------------------------------
    # FILE EXTENSION
    # --------------------------------------------------------

    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if not extension:
        extension = ".jpg"

    # --------------------------------------------------------
    # UNIQUE FILE NAME
    # --------------------------------------------------------

    filename = f"{uuid.uuid4()}{extension}"

    image_path = UPLOAD_DIR / filename

    try:

        # ----------------------------------------------------
        # SAVE IMAGE
        # ----------------------------------------------------

        with open(image_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        print(f"Received image: {filename}")

        # ----------------------------------------------------
        # RUN MODEL
        # ----------------------------------------------------

        result = analyze_ppe(
            str(image_path)
        )

        print(
            f"Analysis complete: "
            f"{result['status']}"
        )

        # ----------------------------------------------------
        # RETURN RESULT
        # ----------------------------------------------------

        return JSONResponse(
            content=result
        )

    except Exception as e:

        print("=" * 60)
        print("PPE ANALYSIS ERROR")
        print("=" * 60)
        print(str(e))
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=f"PPE analysis failed: {str(e)}"
        )

    finally:

        # ----------------------------------------------------
        # DELETE TEMP IMAGE
        # ----------------------------------------------------

        if image_path.exists():

            try:
                image_path.unlink()
            except Exception:
                pass