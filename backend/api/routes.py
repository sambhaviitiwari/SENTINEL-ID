import json
import os
import shutil
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.core.pipeline import run_analysis
from backend.db.database import get_db
from backend.db.models import Case


router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def serialize_case(case):
    return {
        "id": case.id,
        "case_id": case.case_id,
        "filename": case.filename,
        "file_type": case.file_type,
        "file_path": case.file_path,
        "risk_level": case.risk_level,
        "risk_score": case.risk_score,
        "findings": case.findings,
        "analysis_details": (
            json.loads(case.analysis_details)
            if case.analysis_details
            else None
        ),
        "created_at": (
            case.created_at.isoformat()
            if case.created_at
            else None
        ),
    }


@router.get("/status")
def system_status():
    return {
        "system": "SENTINEL-ID",
        "version": "0.1.0",
        "status": "ONLINE",
        "api": "ONLINE",
        "database": "ONLINE",
        "ai_engine": "STANDBY",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/api/v1/analyze")
async def analyze_evidence(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".pdf",
        ".webp",
    }

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}",
        )

    original_filename = os.path.basename(file.filename)
    case_id = f"SNT-{uuid.uuid4().hex[:8].upper()}"
    safe_filename = f"{case_id}_{original_filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = run_analysis(
            file_path=file_path,
            filename=original_filename,
            case_id=case_id,
        )

        # Persist the complete analysis, including module details.
        analysis_details = result.model_dump(mode="json")

        case = Case(
            case_id=result.case_id,
            filename=result.filename,
            file_type=result.file_type,
            file_path=file_path,
            risk_level=result.overall_risk,
            risk_score=result.risk_score,
            findings="\n".join(result.findings),
            analysis_details=json.dumps(analysis_details),
        )

        db.add(case)
        db.commit()
        db.refresh(case)

        return {
            "message": "Evidence analyzed successfully.",
            **serialize_case(case),
            "analyzed_at": result.analyzed_at.isoformat(),
        }

    except Exception:
        db.rollback()

        if os.path.exists(file_path):
            os.remove(file_path)

        raise

    finally:
        await file.close()


@router.get("/api/v1/cases")
def get_cases(db: Session = Depends(get_db)):
    cases = (
        db.query(Case)
        .order_by(Case.created_at.desc())
        .all()
    )

    return {
        "count": len(cases),
        "cases": [
            serialize_case(case)
            for case in cases
        ],
    }


@router.get("/api/v1/cases/{case_id}")
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = (
        db.query(Case)
        .filter(Case.case_id == case_id)
        .first()
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return serialize_case(case)
