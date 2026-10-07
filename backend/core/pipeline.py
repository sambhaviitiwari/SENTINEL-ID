import os
import uuid
from datetime import datetime

from backend.schemas.results import AnalysisResult

from backend.modules.document_analysis.analyzer import analyze_document
from backend.modules.face_analysis.analyzer import analyze_face
from backend.modules.identity_analysis.analyzer import analyze_identity
from backend.modules.synthetic_media.analyzer import analyze_synthetic_media


def calculate_overall_risk(scores: list[float]) -> tuple[str, float]:
    overall_score = round(sum(scores) / len(scores), 2)

    if overall_score >= 70:
        risk_level = "HIGH"
    elif overall_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return risk_level, overall_score


def run_analysis(file_path: str, filename: str) -> AnalysisResult:

    case_id = f"SNT-{uuid.uuid4().hex[:8].upper()}"

    document_result = analyze_document(file_path)
    face_result = analyze_face(file_path)
    identity_result = analyze_identity(file_path)
    synthetic_result = analyze_synthetic_media(file_path)

    scores = [
        document_result.risk_score,
        face_result.risk_score,
        identity_result.risk_score,
        synthetic_result.risk_score,
    ]

    risk_level, overall_score = calculate_overall_risk(scores)

    findings = (
        document_result.findings
        + face_result.findings
        + identity_result.findings
        + synthetic_result.findings
    )

    file_type = os.path.splitext(filename)[1].lower().replace(".", "")

    return AnalysisResult(
        case_id=case_id,
        filename=filename,
        file_type=file_type or "unknown",
        overall_risk=risk_level,
        risk_score=overall_score,
        document_analysis=document_result,
        face_analysis=face_result,
        identity_analysis=identity_result,
        synthetic_media_analysis=synthetic_result,
        findings=findings,
        analyzed_at=datetime.utcnow(),
    )