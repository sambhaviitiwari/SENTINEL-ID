
import hashlib
import os

from backend.schemas.results import ModuleResult


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".pdf",
}


def analyze_synthetic_media(file_path: str) -> ModuleResult:
    details = {
        "analysis_stage": "synthetic_media_baseline_inspection",
        "synthetic_media_detected": None,
        "detection_model_available": False,
        "deepfake_detection_performed": False,
    }

    if not os.path.isfile(file_path):
        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=["Evidence file does not exist."],
            details=details,
        )

    try:
        digest = hashlib.sha256()
        size_bytes = 0

        with open(file_path, "rb") as evidence:
            header = evidence.read(32)
            digest.update(header)
            size_bytes += len(header)

            while True:
                chunk = evidence.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                size_bytes += len(chunk)

        extension = os.path.splitext(file_path)[1].lower()
        supported = extension in SUPPORTED_EXTENSIONS

        details.update({
            "file_extension": extension,
            "size_bytes": size_bytes,
            "sha256": digest.hexdigest(),
            "supported_format": supported,
            "evidence_readable": True,
        })

        findings = [
            "Evidence was readable and its SHA-256 fingerprint was calculated.",
            "File readability and fingerprinting do not establish whether media is synthetic.",
            "No trained synthetic-media or deepfake detection model is configured.",
            "Synthetic-media classification remains inconclusive.",
        ]

        if not supported:
            findings.append(
                "This file extension is outside the configured inspection scope."
            )

        return ModuleResult(
            status="completed",
            risk_score=0.0,
            findings=findings,
            details=details,
        )

    except OSError as exc:
        details["error"] = str(exc)

        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=["Evidence could not be read for synthetic-media inspection."],
            details=details,
        )
