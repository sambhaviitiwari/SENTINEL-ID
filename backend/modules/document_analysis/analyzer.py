
import hashlib
import os
import struct

from backend.schemas.results import ModuleResult


ALLOWED_SIGNATURES = {
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".webp": (b"RIFF",),
    ".pdf": (b"%PDF-",),
}


def analyze_document(file_path: str) -> ModuleResult:
    findings = []
    details = {
        "analysis_stage": "baseline_document_inspection",
        "authenticity_verified": False,
    }
    risk_score = 0.0

    if not os.path.isfile(file_path):
        return ModuleResult(
            status="failed",
            risk_score=0.0,
            findings=["Evidence file does not exist or is not a regular file."],
            details=details,
        )

    try:
        digest = hashlib.sha256()
        size_bytes = 0
        header = b""

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
            findings.append("Evidence file is empty.")
            details["signature_check"] = "failed"
        elif not signatures:
            risk_score += 20
            findings.append(
                "No signature rule is configured for this file extension."
            )
        elif not any(header.startswith(sig) for sig in signatures):
            risk_score += 50
            findings.append(
                "File content signature does not match its filename extension."
            )
            details["signature_check"] = "failed"
        else:
            details["signature_check"] = "passed"
            findings.append(
                "File header matches the expected signature for its extension."
            )

        if extension == ".webp" and len(header) >= 12:
            details["webp_header_check"] = (
                "passed" if header[8:12] == b"WEBP" else "failed"
            )
            if header[8:12] != b"WEBP":
                risk_score += 30
                findings.append("WebP container header is inconsistent.")

        if extension == ".png" and len(header) >= 24:
            width, height = struct.unpack(">II", header[16:24])
            details["image_dimensions"] = {
                "width": width,
                "height": height,
            }
            if width == 0 or height == 0:
                risk_score += 30
                findings.append("PNG image dimensions are invalid.")
            else:
                findings.append(
                    f"PNG dimensions detected: {width} x {height}."
                )

        if extension == ".pdf":
            with open(file_path, "rb") as evidence:
                evidence.seek(max(0, size_bytes - 2048))
                tail = evidence.read()

            details["pdf_end_marker_present"] = b"%%EOF" in tail
            if b"%%EOF" not in tail:
                risk_score += 20
                findings.append(
                    "PDF end marker was not found near the end of the file."
                )
            else:
                findings.append("PDF end marker detected.")

        risk_score = min(100.0, round(risk_score, 2))
        findings.append(
            "This inspection does not establish document authenticity "
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
