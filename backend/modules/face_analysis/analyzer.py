
import os
from pathlib import Path

import cv2
from PIL import Image, UnidentifiedImageError

from backend.schemas.results import ModuleResult


MODEL_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "models"
    / "haarcascade_frontalface_default.xml"
)


def analyze_face(file_path: str) -> ModuleResult:
    findings = []
    details = {
        "analysis_stage": "face_detection",
        "face_detected": None,
        "face_count": 0,
        "face_detection_performed": False,
        "identity_verified": False,
        "detector": "OpenCV Haar Cascade",
    }

    if not os.path.isfile(file_path):
        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=["Evidence file does not exist."],
            details=details,
        )

    if Path(file_path).suffix.lower() not in {
        ".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"
    }:
        details["analysis_stage"] = "skipped_unsupported_format"
        findings.append(
            "Face detection was skipped because this file format "
            "is not supported by the current image detector."
        )
        return ModuleResult(
            status="completed",
            risk_score=0.0,
            findings=findings,
            details=details,
        )

    if not MODEL_PATH.is_file():
        details["model_available"] = False
        findings.append("Face detection model file is unavailable.")
        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=findings,
            details=details,
        )

    try:
        image = cv2.imread(file_path)

        if image is None:
            findings.append(
                "The image could not be decoded by the face detector."
            )
            return ModuleResult(
                status="failed",
                risk_score=0.0,
                findings=findings,
                details=details,
            )

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        detector = cv2.CascadeClassifier(str(MODEL_PATH))

        if detector.empty():
            findings.append("The face detection model could not be loaded.")
            return ModuleResult(
                status="failed",
                risk_score=0.0,
                findings=findings,
                details=details,
            )

        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )

        face_count = len(faces)
        details.update({
            "model_available": True,
            "face_detection_performed": True,
            "face_detected": face_count > 0,
            "face_count": face_count,
            "image_width": int(image.shape[1]),
            "image_height": int(image.shape[0]),
        })

        if face_count:
            findings.append(
                f"Face detector identified {face_count} possible face(s)."
            )
        else:
            findings.append(
                "No face was detected by the current Haar Cascade detector."
            )

        findings.append(
            "Face detection does not verify a person's identity."
        )
        findings.append(
            "Face detection results alone do not establish authenticity "
            "or determine whether media is synthetic."
        )

        return ModuleResult(
            status="completed",
            risk_score=0.0,
            findings=findings,
            details=details,
        )

    except (OSError, ValueError, cv2.error) as exc:
        details["error"] = str(exc)
        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=["Face detection could not be completed for this file."],
            details=details,
        )
