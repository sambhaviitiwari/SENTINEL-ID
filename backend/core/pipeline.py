
import os
import uuid
from datetime import datetime

from backend.schemas.results import AnalysisResult

from backend.modules.document_analysis.analyzer import analyze_document
from backend.modules.face_analysis.analyzer import analyze_face
from backend.modules.identity_analysis.analyzer import analyze_identity
from backend.modules.synthetic_media.analyzer import analyze_synthetic_media


def run_analysis(
    file_path: str,
    filename: str,
    case_id: str | None = None
) -> AnalysisResult:
    case_id = case_id or f"SNT-{uuid.uuid4().hex[:8].upper()}"

    document_result = analyze_document(file_path)
    face_result = analyze_face(file_path)
    identity_result = analyze_identity(file_path)
    synthetic_result = analyze_synthetic_media(file_path)

    # Until trained detection models are integrated, do not present
    # the combined result as a verified overall risk classification.
    overall_risk = "INCONCLUSIVE"

    # This score represents document/file-integrity checks only.
    # It is not a score for identity fraud or synthetic-media detection.
    risk_score = document_result.risk_score

    findings = (
        document_result.findings
        + face_result.findings
        + identity_result.findings
        + synthetic_result.findings
        + [
            "Overall risk classification is inconclusive.",
            "The numeric risk score reflects document/file-integrity checks only.",
            "Face detection, identity verification, and deepfake detection "
            "are not currently performed by trained models.",
        ]
    )

    file_type = os.path.splitext(filename)[1].lower().replace(".", "")

    return AnalysisResult(
        case_id=case_id,
        filename=filename,
        file_type=file_type or "unknown",
        overall_risk=overall_risk,
        risk_score=risk_score,
        document_analysis=document_result,
        face_analysis=face_result,
        identity_analysis=identity_result,
        synthetic_media_analysis=synthetic_result,
        findings=findings,
        analyzed_at=datetime.utcnow(),
    )
