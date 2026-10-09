
import hashlib
import os
from datetime import datetime

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

EXIF_FIELDS = {
    271: "camera_make",
    272: "camera_model",
    306: "datetime",
    36867: "datetime_original",
    36868: "datetime_digitized",
    305: "software",
    315: "artist",
    33432: "copyright",
}


def _safe_metadata_value(value, limit=200):
    """Convert untrusted metadata into a bounded JSON-friendly value."""
    if value is None:
        return None

    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")

    if isinstance(value, str):
        return value[:limit]

    if isinstance(value, (int, float, bool)):
        return value

    return str(value)[:limit]


def _inspect_image_metadata(file_path, details, findings):
    """Extract selected EXIF fields without treating them as verified."""
    try:
        with Image.open(file_path) as image:
            exif = image.getexif()
            extracted = {}

            for tag_id, field_name in EXIF_FIELDS.items():
                value = exif.get(tag_id)

                if value is not None:
                    extracted[field_name] = _safe_metadata_value(value)

        details.update({
            "exif_metadata_present": bool(exif),
            "exif_fields": extracted,
            "exif_field_count": len(extracted),
            "metadata_inspection": "completed",
        })

        if extracted:
            findings.append(
                "Selected image EXIF fields were extracted; their "
                "accuracy and origin have not been verified."
            )
        else:
            findings.append(
                "No selected standard EXIF fields were found."
            )

    except (
        OSError,
        ValueError,
        SyntaxError,
        UnidentifiedImageError,
    ) as exc:
        details["metadata_inspection"] = "partial"
        details["metadata_inspection_error"] = str(exc)[:200]
        findings.append(
            "Image metadata could not be fully inspected."
        )


def _pdf_date_is_parseable(value):
    """Check common PDF date formats without claiming they are authentic."""
    if not isinstance(value, str):
        return False

    cleaned = value.strip()

    if cleaned.startswith("D:"):
        cleaned = cleaned[2:]

    # A PDF date may omit trailing time components.
    # Accept a valid date alone or a date with a complete time.
    try:
        if len(cleaned) >= 14:
            datetime.strptime(cleaned[:14], "%Y%m%d%H%M%S")
        elif len(cleaned) >= 8:
            datetime.strptime(cleaned[:8], "%Y%m%d")
        else:
            return False

        return True

    except ValueError:
        return False


def _inspect_pdf_metadata(file_path, details, findings):
    """Extract standard PDF metadata; values remain unverified."""
    try:
        reader = PdfReader(file_path, strict=True)
        metadata = reader.metadata
        fields = {}

        metadata_map = {
            "title": "/Title",
            "author": "/Author",
            "subject": "/Subject",
            "creator": "/Creator",
            "producer": "/Producer",
            "creation_date": "/CreationDate",
            "modification_date": "/ModDate",
        }

        if metadata:
            for output_key, pdf_key in metadata_map.items():
                value = metadata.get(pdf_key)

                if value is not None:
                    fields[output_key] = _safe_metadata_value(value)

        details["pdf_metadata_present"] = bool(fields)
        details["pdf_metadata"] = fields

        for date_key in ("creation_date", "modification_date"):
            if date_key in fields:
                details[f"{date_key}_parseable"] = (
                    _pdf_date_is_parseable(fields[date_key])
                )

        details["metadata_inspection"] = "completed"

        if fields:
            findings.append(
                "PDF metadata fields were extracted; their accuracy "
                "and origin have not been verified."
            )
        else:
            findings.append(
                "No standard PDF document metadata was found."
            )

    except Exception as exc:
        # Metadata is supplementary. A metadata failure alone should
        # not invalidate successful structural validation.
        details["metadata_inspection"] = "partial"
        details["pdf_metadata_error"] = str(exc)[:200]
        findings.append(
            "PDF metadata could not be fully inspected."
        )


def analyze_document(file_path: str) -> ModuleResult:
    """Inspect file integrity, structure, and selected metadata."""
    findings = []
    details = {
        "analysis_stage": "structural_document_inspection",
        "authenticity_verified": False,
        "authenticity_status": "not_verified",
        "structural_validation": "not_run",
        "metadata_inspection": "not_run",
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
        header = b""

        # Calculate the evidence hash and capture the file signature.
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

        # Check whether the file signature matches its extension.
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

        # Parse only supported file types with matching signatures.
        if (
            size_bytes > 0
            and signatures
            and details["signature_check"] == "passed"
        ):
            if extension in IMAGE_EXTENSIONS:
                try:
                    # verify() checks image structure but does not decode
                    # all pixels, so reopen the image and load it.
                    with Image.open(file_path) as image:
                        image_format = image.format
                        image.verify()

                    with Image.open(file_path) as image:
                        image.load()
                        width, height = image.size
                        color_mode = image.mode

                    details.update({
                        "structural_validation": "passed",
                        "image_format_detected": image_format,
                        "image_dimensions": {
                            "width": width,
                            "height": height,
                        },
                        "image_color_mode": color_mode,
                    })

                    findings.append(
                        "Image structure validated and pixel data decoded."
                    )

                    if width <= 0 or height <= 0:
                        risk_score += 30
                        details["structural_validation"] = "failed"
                        findings.append(
                            "Image dimensions are invalid."
                        )

                    _inspect_image_metadata(
                        file_path,
                        details,
                        findings,
                    )

                except (
                    UnidentifiedImageError,
                    OSError,
                    SyntaxError,
                    ValueError,
                ) as exc:
                    risk_score += 40
                    details["structural_validation"] = "failed"
                    details["image_validation_error"] = str(exc)[:300]
                    details["metadata_inspection"] = "not_run"

                    findings.append(
                        "Image structure validation failed; the image may "
                        "be truncated, malformed, or unsupported."
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
                        findings.append(
                            "PDF contains no pages."
                        )

                    # Look for the PDF end marker near the file's end.
                    with open(file_path, "rb") as evidence:
                        evidence.seek(max(0, size_bytes - 2048))
                        tail = evidence.read()

                    eof_present = b"%%EOF" in tail
                    details["pdf_end_marker_present"] = eof_present

                    if eof_present:
                        findings.append("PDF end marker detected.")
                    else:
                        risk_score += 20
                        findings.append(
                            "PDF end marker was not found near the end "
                            "of the file."
                        )

                    _inspect_pdf_metadata(
                        file_path,
                        details,
                        findings,
                    )

                except Exception as exc:
                    risk_score += 40
                    details["structural_validation"] = "failed"
                    details["pdf_validation_error"] = str(exc)[:300]
                    details["metadata_inspection"] = "not_run"

                    findings.append(
                        "PDF structural parsing failed; the file may be "
                        "malformed, incomplete, encrypted, or unsupported."
                    )

        risk_score = min(100.0, round(risk_score, 2))

        findings.append(
            "Structural checks and metadata inspection do not prove "
            "document authenticity or detect every form of manipulation."
        )

        return ModuleResult(
            status="completed",
            risk_score=risk_score,
            findings=findings,
            details=details,
        )

    except OSError as exc:
        details["analysis_error"] = str(exc)[:300]

        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=[
                "Evidence could not be read due to a file-system error."
            ],
            details=details,
        )
