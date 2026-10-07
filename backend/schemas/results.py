from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ModuleResult(BaseModel):
    status: str = "pending"
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    findings: List[str] = []
    details: Dict[str, Any] = {}


class AnalysisResult(BaseModel):
    case_id: str
    filename: str
    file_type: str

    overall_risk: str
    risk_score: float = Field(ge=0.0, le=100.0)

    document_analysis: ModuleResult
    face_analysis: ModuleResult
    identity_analysis: ModuleResult
    synthetic_media_analysis: ModuleResult

    findings: List[str] = []
    analyzed_at: datetime