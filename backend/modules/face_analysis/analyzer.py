from backend.schemas.results import ModuleResult


def analyze_face(file_path: str) -> ModuleResult:
    return ModuleResult(
        status="completed",
        risk_score=5.0,
        findings=[
            "Face analysis module initialized.",
            "No biometric comparison performed in baseline mode."
        ],
        details={
            "analysis_stage": "baseline"
        }
    )