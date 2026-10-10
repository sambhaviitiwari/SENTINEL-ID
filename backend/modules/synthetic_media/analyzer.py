
import hashlib
import os
from functools import lru_cache
from pathlib import Path

import cv2
import torch
from PIL import Image

from transformers import AutoFeatureExtractor, AutoModelForImageClassification

from backend.schemas.results import ModuleResult


MODEL_ID = "agasta/virtus"
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"
}
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | {".pdf"}

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FACE_CASCADE_PATH = (
    PROJECT_ROOT / "data" / "models" / "haarcascade_frontalface_default.xml"
)


@lru_cache(maxsize=1)
def load_classifier():
    """Load and cache the experimental classifier once per process."""
    torch.set_num_threads(2)

    processor = AutoFeatureExtractor.from_pretrained(
        MODEL_ID,
        local_files_only=True,
    )
    model = AutoModelForImageClassification.from_pretrained(
        MODEL_ID,
        local_files_only=True,
    )
    model.eval()
    model.to("cpu")

    return processor, model


def analyze_synthetic_media(file_path: str) -> ModuleResult:
    details = {
        "analysis_stage": "synthetic_media_baseline_inspection",
        "synthetic_media_detected": None,
        "synthetic_media_prediction": None,
        "prediction_confidence_percent": None,
        "class_probabilities": None,
        "detection_model_available": False,
        "deepfake_detection_performed": False,
        "face_detection_performed": False,
        "face_count": 0,
        "model_name": MODEL_ID,
        "model_mode": "experimental_research",
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
            while True:
                chunk = evidence.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                size_bytes += len(chunk)

        extension = Path(file_path).suffix.lower()
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
            "A file fingerprint does not establish whether media is authentic.",
        ]

        if extension not in IMAGE_EXTENSIONS:
            details["deepfake_skip_reason"] = (
                "Face-specific classification is only configured for raster images."
            )
            findings.append(
                "Face-specific synthetic-media classification was not run "
                "because this file is not a supported raster image."
            )
        else:
            image = cv2.imread(file_path)

            if image is None:
                details["deepfake_skip_reason"] = (
                    "OpenCV could not decode the image."
                )
                findings.append(
                    "The image could not be decoded for face analysis."
                )
            else:
                height, width = image.shape[:2]
                details["image_dimensions"] = {
                    "width": width,
                    "height": height,
                }

                cascade = cv2.CascadeClassifier(str(FACE_CASCADE_PATH))

                if cascade.empty():
                    raise RuntimeError(
                        f"Face detection model could not be loaded: "
                        f"{FACE_CASCADE_PATH}"
                    )

                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30),
                )

                details.update({
                    "face_detection_performed": True,
                    "face_count": int(len(faces)),
                    "face_detector": "OpenCV Haar Cascade",
                })

                if len(faces) == 0:
                    details["deepfake_skip_reason"] = (
                        "No face was detected; face-specific classification skipped."
                    )
                    findings.append(
                        "No face was detected. Face-specific synthetic-media "
                        "classification was not performed."
                    )
                else:
                    # Classify the largest detected face only.
                    x, y, w, h = max(
                        faces,
                        key=lambda box: int(box[2]) * int(box[3]),
                    )

                    face_bgr = image[y:y + h, x:x + w]
                    face_rgb = cv2.cvtColor(
                        face_bgr,
                        cv2.COLOR_BGR2RGB,
                    )
                    face_image = Image.fromarray(face_rgb)

                    try:
                        processor, model = load_classifier()
                        details["detection_model_available"] = True

                        inputs = processor(
                            images=face_image,
                            return_tensors="pt",
                        )

                        with torch.inference_mode():
                            outputs = model(**inputs)
                            probabilities = torch.softmax(
                                outputs.logits,
                                dim=-1,
                            )[0]

                        predicted_index = int(
                            probabilities.argmax().item()
                        )
                        predicted_label = model.config.id2label[
                            predicted_index
                        ]
                        confidence = float(
                            probabilities[predicted_index].item()
                        ) * 100

                        class_probabilities = {
                            model.config.id2label[i]: round(
                                float(probabilities[i].item()) * 100,
                                2,
                            )
                            for i in range(len(probabilities))
                        }

                        details.update({
                            "deepfake_detection_performed": True,
                            "synthetic_media_prediction": predicted_label,
                            "prediction_confidence_percent": round(
                                confidence, 2
                            ),
                            "class_probabilities": class_probabilities,
                            "classified_face_count": 1,
                            "classifier_scope": "largest_detected_face",
                        })

                        findings.append(
                            f"Experimental face classifier prediction: "
                            f"{predicted_label} "
                            f"({confidence:.2f}% model confidence)."
                        )
                        findings.append(
                            "The model prediction is not proof of authenticity "
                            "or manipulation and has not been independently validated."
                        )

                    except Exception as exc:
                        details["classifier_error"] = (
                            f"{type(exc).__name__}: {exc}"
                        )
                        details["deepfake_skip_reason"] = (
                            "Experimental classifier inference failed."
                        )
                        findings.append(
                            "Experimental face classification could not "
                            "be completed; see diagnostic details."
                        )

        if not supported:
            findings.append(
                "This file extension is outside the configured inspection scope."
            )

        findings.append(
            "Overall synthetic-media authenticity remains inconclusive."
        )

        return ModuleResult(
            status="completed",
            risk_score=0.0,
            findings=findings,
            details=details,
        )

    except Exception as exc:
        details["error"] = f"{type(exc).__name__}: {exc}"

        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=[
                "Synthetic-media inspection encountered an error.",
                "No authenticity conclusion was established.",
            ],
            details=details,
        )
