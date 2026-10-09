
import hashlib
import os
import struct

from PIL import Image, UnidentifiedImageError
from pypdf import PdfReader

from backend.schemas.results import ModuleResult


ALLOWED_SIGNATURES = {
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".webp": (b"RIFF",),
    ".pdf": (b"%PDF-",),
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def analyze_document(file_path: str) -> ModuleResult:
    findings = []
    details = {
        "analysis_stage": "structural_document_inspection",
        "authenticity_verified": False,
        "authenticity_status": "not_verified",
        "structural_validation": "not_run",
    }
    risk_score = 0.0

    if not os.path.isfile(file_path):
        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=[
                "Evidence file does not exist or is not a regular file."
            ],
            details=details,
        )

    extension = os.path.splitext(file_path)[1].lower()

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

        signatures = ALLOWED_SIGNATURES.get(extension)

        details.update({
            "file_extension": extension,
            "size_bytes": size_bytes,
            "sha256": digest.hexdigest(),
            "signature_check": "not_supported",
        })

        findings.append("Evidence file was readable.")
        findings.append("SHA-256 evidence hash calculated successfully.")

        if size_bytes == 0:
            risk_score += 60
            details["signature_check"] = "failed"
            findings.append("Evidence file is empty.")

        elif not signatures:
            risk_score += 20
            findings.append(
                "No signature rule is configured for this file extension."
            )

        elif not any(header.startswith(sig) for sig in signatures):
            risk_score += 50
            details["signature_check"] = "failed"
            findings.append(
                "File content signature does not match its filename extension."
            )

        else:
            details["signature_check"] = "passed"
            findings.append(
                "File header matches the expected signature for its extension."
            )

        if size_bytes > 0 and signatures and details["signature_check"] == "passed":
            if extension in IMAGE_EXTENSIONS:
                try:
                    with Image.open(file_path) as image:
                        image_format = image.format
                        image.verify()

                    # Reopen after verify; Pillow's verify() invalidates
                    # the image object for further decoding.
                    with Image.open(file_path) as image:
                        image.load()
                        width, height = image.size

                    details.update({
                        "structural_validation": "passed",
                        "image_format_detected": image_format,
                        "image_dimensions": {
                            "width": width,
                            "height": height,
                        },
                    })
                    findings.append(
                        "Image structure validated and pixel data decoded."
                    )

                    if width <= 0 or height <= 0:
                        risk_score += 30
                        details["structural_validation"] = "failed"
                        findings.append("Image dimensions are invalid.")

                except (UnidentifiedImageError, OSError, SyntaxError, ValueError) as exc:
                    risk_score += 40
                    details["structural_validation"] = "failed"
                    details["image_validation_error"] = str(exc)[:300]
                    findings.append(
                        "Image structure validation failed; the image "
                        "may be truncated, malformed, or unsupported."
                    )

                if extension == ".webp":
                    with open(file_path, "rb") as evidence:
                        webp_header = evidence.read(12)

                    details["webp_header_check"] = (
                        "passed"
                        if len(webp_header) >= 12
                        and webp_header[8:12] == b"WEBP"
                        else "failed"
                    )

                    if details["webp_header_check"] == "failed":
                        risk_score += 30
                        findings.append(
                            "WebP container header is inconsistent."
                        )

            elif extension == ".pdf":
                try:
                    reader = PdfReader(file_path, strict=True)
                    page_count = len(reader.pages)

                    details.update({
                        "structural_validation": "passed",
                        "pdf_page_count": page_count,
                        "pdf_is_encrypted": reader.is_encrypted,
                    })
                    findings.append(
                        f"PDF structure parsed successfully; "
                        f"{page_count} page(s) detected."
                    )

                    if page_count == 0:
                        risk_score += 30
                        findings.append("PDF contains no pages.")

                    with open(file_path, "rb") as evidence:
                        evidence.seek(max(0, size_bytes - 2048))
                        tail = evidence.read()

                    details["pdf_end_marker_present"] = b"%%EOF" in tail

                    if not details["pdf_end_marker_present"]:
                        risk_score += 20
                        findings.append(
                            "PDF end marker was not found near the end "
                            "of the file."
                        )
                    else:
                        findings.append("PDF end marker detected.")

                except Exception as exc:
                    risk_score += 40
                    details["structural_validation"] = "failed"
                    details["pdf_validation_error"] = str(exc)[:300]
                    findings.append(
                        "PDF structural parsing failed; the file may be "
                        "malformed, incomplete, encrypted, or unsupported."
                    )

        risk_score = min(100.0, round(risk_score, 2))

        findings.append(
            "Structural validation does not prove document authenticity "
            "or detect all forms of manipulation."
        )

        return ModuleResult(
            status="completed",
            risk_score=risk_score,
            findings=findings,
            details=details,
        )

    except OSError as exc:
        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=[f"Evidence could not be read: {exc}"],
            details=details,
        )
