
import os

from PIL import Image, UnidentifiedImageError

from backend.schemas.results import ModuleResult


def analyze_face(file_path: str) -> ModuleResult:
    findings = []
    details = {
        "analysis_stage": "image_validation",
        "face_detected": None,
        "identity_verified": False,
    }

    if not os.path.isfile(file_path):
        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=["Image file does not exist."],
            details=details,
        )

    try:
        with Image.open(file_path) as image:
            image_format = image.format
            width, height = image.size
            image.verify()

        details.update({
            "image_format": image_format,
            "width": width,
            "height": height,
            "face_detection_performed": False,
        })

        findings.append("Image opened and passed Pillow's integrity check.")
        findings.append(
            f"Image dimensions: {width} x {height} pixels."
        )
        findings.append(
            "Face detection was not performed: no face-detection model "
            "is configured."
        )
        findings.append(
            "Identity verification was not performed."
        )

        return ModuleResult(
            status="completed",
            risk_score=0.0,
            findings=findings,
            details=details,
        )

    except (UnidentifiedImageError, OSError, ValueError) as exc:
        details["error"] = str(exc)

        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=[
                "The file could not be validated as a readable image."
            ],
            details=details,
        )
