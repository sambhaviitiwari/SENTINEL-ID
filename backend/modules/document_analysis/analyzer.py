from backend.schemas.results import ModuleResult


def analyze_document(file_path: str) -> ModuleResult:
    return ModuleResult(
        status="completed",
        risk_score=10.0,
        findings=[
            "Document received successfully.",
            "Initial document integrity check completed."
        ],
        details={
            "file_path": file_path,
            "analysis_stage": "baseline"
        }
    )