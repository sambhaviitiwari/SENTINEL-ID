
import os
import uuid
from datetime import datetime, timezone

from backend.schemas.results import AnalysisResult
from backend.modules.document_analysis.analyzer import analyze_document
from backend.modules.face_analysis.analyzer import analyze_face
from backend.modules.identity_analysis.analyzer import analyze_identity
from backend.modules.synthetic_media.analyzer import analyze_synthetic_media


def run_analysis(
    file_path: str,
    filename: str,
    case_id: str | None = None,
) -> AnalysisResult:
    case_id = case_id or f"SNT-{uuid.uuid4().hex[:8].upper()}"

    # Run all analysis modules.
    document_result = analyze_document(file_path)
    face_result = analyze_face(file_path)
    identity_result = analyze_identity(file_path)
    synthetic_result = analyze_synthetic_media(file_path)

    # The risk score reflects document/file-integrity checks only.
    risk_score = document_result.risk_score

    # Keep the overall classification conservative until the models
    # have been independently validated.
    overall_risk = "INCONCLUSIVE"

    # Build concise case-level findings.
    findings = [
        "Analysis completed for the submitted evidence.",
        (
            "Document structural inspection completed."
            if document_result.status == "completed"
            else "Document structural inspection did not complete successfully."
        ),
    ]

    # Face detection findings.
    if face_result.details.get("face_detection_performed"):
        face_count = face_result.details.get("face_count", 0)
        findings.append(
            f"OpenCV Haar Cascade face detection completed: "
            f"{face_count} possible face(s) detected."
        )
    else:
        findings.append(
            "Face detection was not completed for this evidence."
        )

    # Identity verification findings.
    identity_verified = identity_result.details.get("identity_verified")
    identity_performed = identity_result.details.get(
        "cross_modal_verification_performed", False
    )

    if identity_performed:
        findings.append(
            "Identity verification result: "
            f"{'verified' if identity_verified else 'not verified'}."
        )
    else:
        findings.append(
            "Identity verification was not performed against a trusted reference."
        )

    # Experimental synthetic-media classification findings.
    deepfake_performed = synthetic_result.details.get(
        "deepfake_detection_performed", False
    )
    prediction = synthetic_result.details.get(
        "synthetic_media_prediction"
    )
    confidence = synthetic_result.details.get(
        "prediction_confidence_percent"
    )

    if deepfake_performed and prediction is not None:
        if isinstance(confidence, (int, float)):
            findings.append(
                f"Experimental face classifier prediction: {prediction} "
                f"({confidence:.2f}% model confidence)."
            )
        else:
            findings.append(
                f"Experimental face classifier prediction: {prediction}."
            )

        findings.append(
            "The model prediction is experimental and does not establish "
            "whether the evidence is authentic or manipulated."
        )
    else:
        skip_reason = synthetic_result.details.get(
            "deepfake_skip_reason"
        )

        if skip_reason:
            findings.append(str(skip_reason))
        else:
            findings.append(
                "Synthetic-media classification was not performed."
            )

    # Final case-level qualification.
    findings.extend([
        "Overall risk classification remains INCONCLUSIVE.",
        (
            "The risk score reflects document/file-integrity checks only; "
            "it is not a probability of fraud."
        ),
    ])

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
        analyzed_at=datetime.now(timezone.utc),
    )
