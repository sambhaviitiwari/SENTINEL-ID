import os
import shutil
import uuid

from fastapi import APIRouter, File, UploadFile, HTTPException

from backend.core.pipeline import run_analysis


router = APIRouter(
    prefix="/api/v1",
    tags=["Analysis"]
)


UPLOAD_DIR = "data/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/analyze")
async def analyze_evidence(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided."
        )

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".pdf",
        ".webp"
    }

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
        )

    case_id = f"SNT-{uuid.uuid4().hex[:8].upper()}"

    safe_filename = f"{case_id}_{file.filename}"

    file_path = os.path.join(
        UPLOAD_DIR,
        safe_filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = run_analysis(
        file_path=file_path,
        filename=file.filename
    )

    return result