import hashlib
import json
import os
import shutil
import uuid
from datetime import datetime
from html import escape
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.core.pipeline import run_analysis
from backend.db.database import get_db
from backend.db.models import Case


router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def serialize_case(case):
    """Convert a database case into a JSON-serializable dictionary."""
    try:
        analysis_details = (
            json.loads(case.analysis_details)
            if case.analysis_details
            else None
        )
    except (json.JSONDecodeError, TypeError):
        analysis_details = None

    return {
        "id": case.id,
        "case_id": case.case_id,
        "filename": case.filename,
        "file_type": case.file_type,
        "file_path": case.file_path,
        "risk_level": case.risk_level,
        "risk_score": case.risk_score,
        "findings": case.findings,
        "analysis_details": analysis_details,
        "created_at": (
            case.created_at.isoformat()
            if case.created_at
            else None
        ),
    }


def _report_value(value):
    """Convert values into readable report text."""
    if value is None:
        return "Not available"

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, (dict, list)):
        return json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        )

    return str(value)


def _flatten_analysis(value, prefix="", rows=None):
    """Flatten nested analysis data into table rows."""
    if rows is None:
        rows = []

    if len(rows) >= 80:
        return rows

    if isinstance(value, dict):
        for key, item in value.items():
            if len(rows) >= 80:
                break

            label = f"{prefix} / {key}" if prefix else str(key)

            if isinstance(item, (dict, list)):
                _flatten_analysis(item, label, rows)
            else:
                rows.append((label, _report_value(item)))

    elif isinstance(value, list):
        for index, item in enumerate(value):
            if len(rows) >= 80:
                break

            label = f"{prefix} [{index + 1}]"

            if isinstance(item, (dict, list)):
                _flatten_analysis(item, label, rows)
            else:
                rows.append((label, _report_value(item)))

    elif prefix:
        rows.append((prefix, _report_value(value)))

    return rows


@router.get("/status")
def system_status():
    return {
        "system": "SENTINEL-ID",
        "version": "0.1.0",
        "status": "ONLINE",
        "api": "ONLINE",
        "database": "ONLINE",
        "ai_engine": "STANDBY",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/api/v1/analyze")
async def analyze_evidence(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".pdf",
        ".webp",
    }

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}",
        )

    original_filename = os.path.basename(file.filename)
    case_id = f"SNT-{uuid.uuid4().hex[:8].upper()}"
    safe_filename = f"{case_id}_{original_filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = run_analysis(
            file_path=file_path,
            filename=original_filename,
            case_id=case_id,
        )

        analysis_details = result.model_dump(mode="json")

        case = Case(
            case_id=result.case_id,
            filename=result.filename,
            file_type=result.file_type,
            file_path=file_path,
            risk_level=result.overall_risk,
            risk_score=result.risk_score,
            findings="\n".join(result.findings),
            analysis_details=json.dumps(analysis_details),
        )

        db.add(case)
        db.commit()
        db.refresh(case)

        return {
            "message": "Evidence analyzed successfully.",
            **serialize_case(case),
            "analyzed_at": result.analyzed_at.isoformat(),
        }

    except Exception:
        db.rollback()

        if os.path.exists(file_path):
            os.remove(file_path)

        raise

    finally:
        await file.close()


@router.get("/api/v1/cases")
def get_cases(db: Session = Depends(get_db)):
    cases = (
        db.query(Case)
        .order_by(Case.created_at.desc())
        .all()
    )

    return {
        "count": len(cases),
        "cases": [
            serialize_case(case)
            for case in cases
        ],
    }


@router.get("/api/v1/cases/{case_id}")
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = (
        db.query(Case)
        .filter(Case.case_id == case_id)
        .first()
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return serialize_case(case)


@router.get("/api/v1/cases/{case_id}/report")
def download_case_report(
    case_id: str,
    db: Session = Depends(get_db),
):
    """Generate a downloadable PDF report for a registered case."""

    case = (
        db.query(Case)
        .filter(Case.case_id == case_id)
        .first()
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    try:
        details = (
            json.loads(case.analysis_details)
            if case.analysis_details
            else {}
        )
    except (json.JSONDecodeError, TypeError):
        details = {}

    if not isinstance(details, dict):
        details = {}

    evidence_exists = (
        bool(case.file_path)
        and os.path.isfile(case.file_path)
    )

    evidence_hash = "Unavailable: evidence file missing"
    evidence_size = "Unavailable"

    if evidence_exists:
        digest = hashlib.sha256()
        size = 0

        try:
            with open(case.file_path, "rb") as evidence:
                for chunk in iter(
                    lambda: evidence.read(1024 * 1024),
                    b"",
                ):
                    digest.update(chunk)
                    size += len(chunk)

            evidence_hash = digest.hexdigest()
            evidence_size = f"{size:,} bytes"

        except OSError:
            evidence_hash = "Unavailable: could not read evidence"
            evidence_size = "Unavailable"

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"SENTINEL-ID Investigation Report - {case.case_id}",
        author="SENTINEL-ID",
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="SentinelTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=25,
            textColor=colors.HexColor("#14213D"),
            alignment=1,
            spaceAfter=5 * mm,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0B6E75"),
            spaceBefore=5 * mm,
            spaceAfter=2 * mm,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallText",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11,
            wordWrap="CJK",
        )
    )

    styles.add(
        ParagraphStyle(
            name="HashText",
            parent=styles["BodyText"],
            fontSize=7,
            leading=10,
            wordWrap="CJK",
        )
    )

    def paragraph(value, style="SmallText"):
        safe_text = escape(_report_value(value))
        safe_text = safe_text.replace("\n", "<br/>")
        return Paragraph(safe_text, styles[style])

    def make_table(data, widths):
        table = Table(
            [
                [paragraph(cell) for cell in row]
                for row in data
            ],
            colWidths=widths,
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#14213D"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#D5DCE5"),
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (0, -1),
                        colors.HexColor("#EEF2F7"),
                    ),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        return table

    report_time = datetime.utcnow().strftime(
        "%d %B %Y, %H:%M UTC"
    )

    story = [
        Paragraph("SENTINEL-ID", styles["SentinelTitle"]),
        Paragraph(
            "DIGITAL EVIDENCE INVESTIGATION REPORT",
            styles["Heading2"],
        ),
        Spacer(1, 3 * mm),
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#0B6E75"),
        ),
        Spacer(1, 4 * mm),
        Paragraph("CASE SUMMARY", styles["SectionHeading"]),
    ]

    summary_rows = [
        ["Field", "Value"],
        ["Case ID", case.case_id],
        ["Evidence filename", case.filename],
        ["File type", case.file_type],
        [
            "Case created",
            case.created_at.isoformat()
            if case.created_at
            else "Not available",
        ],
        ["Report generated", report_time],
        ["Risk classification", case.risk_level],
        ["Risk score", f"{case.risk_score:.2f}"],
    ]

    story.extend(
        [
            make_table(summary_rows, [48 * mm, 116 * mm]),
            Spacer(1, 3 * mm),
            Paragraph(
                "EVIDENCE INTEGRITY",
                styles["SectionHeading"],
            ),
        ]
    )

    integrity_rows = [
        ["Property", "Value"],
        ["Evidence file available", "Yes" if evidence_exists else "No"],
        ["Current file size", evidence_size],
        ["SHA-256", evidence_hash],
    ]

    integrity_table = Table(
        [
            [
                paragraph(cell, "HashText" if row_index == 3 and cell_index == 1 else "SmallText")
                for cell_index, cell in enumerate(row)
            ]
            for row_index, row in enumerate(integrity_rows)
        ],
        colWidths=[48 * mm, 116 * mm],
        repeatRows=1,
    )

    integrity_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#14213D"),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D5DCE5"),
                ),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.extend(
        [
            integrity_table,
            Spacer(1, 3 * mm),
            Paragraph(
                "ANALYSIS FINDINGS",
                styles["SectionHeading"],
            ),
        ]
    )

    if case.findings:
        for finding in case.findings.splitlines():
            if finding.strip():
                story.append(
                    Paragraph(
                        "• " + escape(finding),
                        styles["SmallText"],
                    )
                )
                story.append(Spacer(1, 1.5 * mm))
    else:
        story.append(
            paragraph("No stored findings are available for this case.")
        )

    story.append(
        Paragraph(
            "MODULE ANALYSIS DETAILS",
            styles["SectionHeading"],
        )
    )

    analysis_rows = _flatten_analysis(details)

    if analysis_rows:
        module_data = [
            ["Analysis field", "Recorded result"],
            *analysis_rows,
        ]

        module_table = Table(
            [
                [paragraph(cell) for cell in row]
                for row in module_data
            ],
            colWidths=[65 * mm, 99 * mm],
            repeatRows=1,
        )

        module_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#14213D"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#D5DCE5"),
                    ),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        story.append(module_table)
    else:
        story.append(
            paragraph(
                "Detailed analysis data is unavailable. "
                "This may be a legacy case."
            )
        )

    story.append(
        Paragraph(
            "INTERPRETATION & LIMITATIONS",
            styles["SectionHeading"],
        )
    )

    limitations = [
        "This report summarizes automated analysis recorded by SENTINEL-ID.",
        "A risk score is a system-generated indicator, not a probability of fraud.",
        "INCONCLUSIVE means the available checks did not establish a reliable conclusion.",
        "A readable document, matching file signature, or detected face does not prove authenticity or identity.",
        "The SHA-256 value is calculated from the evidence file currently stored on disk. It does not establish who created the file or whether it was authentic before ingestion.",
        "Experimental AI model outputs may be inaccurate and require independent verification.",
        "This report is not a substitute for expert forensic examination or an official identity decision.",
    ]

    for limitation in limitations:
        story.append(
            Paragraph(
                "• " + escape(limitation),
                styles["SmallText"],
            )
        )
        story.append(Spacer(1, 1.5 * mm))

    story.extend(
        [
            Spacer(1, 5 * mm),
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.HexColor("#D5DCE5"),
            ),
            Spacer(1, 2 * mm),
            paragraph(
                "SENTINEL-ID | Generated automatically | "
                "Handle evidence and reports according to applicable "
                "privacy and evidence-retention requirements."
            ),
        ]
    )

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    safe_case_id = "".join(
        character
        for character in case.case_id
        if character.isalnum() or character in "-_"
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="SENTINEL-ID-{safe_case_id}-report.pdf"'
            ),
            "Cache-Control": "no-store",
        },
    )
