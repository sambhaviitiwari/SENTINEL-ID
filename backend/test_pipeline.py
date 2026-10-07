from backend.core.pipeline import run_analysis


result = run_analysis(
    file_path="data/sample_identity_document.jpg",
    filename="sample_identity_document.jpg"
)

print("\n===== SENTINEL-ID ANALYSIS =====")
print(f"Case ID      : {result.case_id}")
print(f"Filename     : {result.filename}")
print(f"Risk Level   : {result.overall_risk}")
print(f"Risk Score   : {result.risk_score}")
print("\nFindings:")

for finding in result.findings:
    print(f"- {finding}")