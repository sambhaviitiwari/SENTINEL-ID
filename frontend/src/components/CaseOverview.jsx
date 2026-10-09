import {
  ArrowUpRight,
  Clock3,
  FileImage,
  Fingerprint,
  ScanSearch,
  ShieldAlert,
  Sparkles,
} from "lucide-react";

function CaseOverview({ caseData }) {
  const currentCase = caseData || {
    case_id: "NO CASE SELECTED",
    filename: "No evidence selected",
    file_type: "unknown",
    risk_level: "INCONCLUSIVE",
    risk_score: null,
    created_at: null,
    findings: "",
  };

  const findings = Array.isArray(currentCase.findings)
    ? currentCase.findings.join("\n").toLowerCase()
    : String(currentCase.findings || "").toLowerCase();

  // Only trust assessments explicitly marked inconclusive by the current pipeline.
  const hasCurrentAssessment = findings.includes(
    "overall risk classification is inconclusive"
  );

  // Older baseline results are not validated risk assessments.
  const riskLevel = hasCurrentAssessment
    ? currentCase.risk_level || "INCONCLUSIVE"
    : "INCONCLUSIVE";

  const parsedScore = Number(currentCase.risk_score);

  const hasValidScore =
    hasCurrentAssessment &&
    currentCase.risk_score !== null &&
    currentCase.risk_score !== undefined &&
    currentCase.risk_score !== "" &&
    Number.isFinite(parsedScore);

  const scoreDisplay = hasValidScore ? parsedScore.toFixed(2) : "—";

  const scorePosition = hasValidScore
    ? Math.min(Math.max(parsedScore, 0), 100)
    : 0;

  const hashCalculated =
    findings.includes("sha-256 evidence hash calculated successfully") ||
    findings.includes("sha-256 fingerprint was calculated");

  return (
    <section className="case-overview">
      <div className="case-heading">
        <div>
          <div className="eyebrow-row">
            <span className="eyebrow">ACTIVE INVESTIGATION</span>
            <span className="case-live">
              <span />
              {caseData ? "CASE LOADED" : "AWAITING CASE"}
            </span>
          </div>

          <h1>{currentCase.case_id}</h1>

          <div className="case-meta">
            <span>{currentCase.filename}</span>
            <span className="meta-divider">/</span>
            <span>
              {String(currentCase.file_type || "unknown").toUpperCase()}
            </span>
            <span className="meta-divider">/</span>
            <span>IDENTITY ANALYSIS</span>
          </div>
        </div>

        <button className="case-action" type="button">
          OPEN CASE
          <ArrowUpRight size={15} />
        </button>
      </div>

      <div className="case-grid">
        <div className="evidence-panel">
          <div className="panel-label">
            <span>EVIDENCE PREVIEW</span>
            <span className="panel-index">01 / 04</span>
          </div>

          <div className="evidence-preview">
            <div className="corner top-left" />
            <div className="corner top-right" />
            <div className="corner bottom-left" />
            <div className="corner bottom-right" />

            <div className="evidence-placeholder">
              <FileImage size={42} strokeWidth={1.1} />

              <span>VISUAL EVIDENCE</span>

              <small>
                {String(currentCase.file_type || "unknown").toUpperCase()}
                {" // SOURCE FILE"}
              </small>
            </div>

            <div className="evidence-scan-line" />

            <div className="evidence-coordinates">
              <span>IMG.001</span>
              <span>LOCAL SOURCE</span>
            </div>
          </div>

          <div className="evidence-footer">
            <span>
              <Clock3 size={12} />
              RECEIVED {formatTime(currentCase.created_at)}
            </span>

            <span>
              {hashCalculated
                ? "SHA-256 CALCULATED"
                : "HASH STATUS UNKNOWN"}
            </span>
          </div>
        </div>

        <div className="risk-panel">
          <div className="panel-label">
            <span>THREAT ASSESSMENT</span>
            <ShieldAlert size={15} />
          </div>

          <div className="risk-display">
            <div className="risk-number">{scoreDisplay}</div>

            <div className={`risk-level ${riskLevel.toLowerCase()}`}>
              <span />
              {riskLevel}
            </div>

            <p>
              {hasValidScore
                ? "File-integrity check score only. This is not a verified identity-fraud or synthetic-media risk score."
                : "No validated overall risk score is available. Previous baseline results are treated as inconclusive."}
            </p>
          </div>

          <div className="risk-scale">
            <div className="scale-track">
              {hasValidScore && (
                <span
                  className="scale-marker"
                  style={{ left: `${scorePosition}%` }}
                />
              )}
            </div>

            <div className="scale-labels">
              <span>LOW</span>
              <span>MEDIUM</span>
              <span>HIGH</span>
              <span>CRITICAL</span>
            </div>
          </div>

          <div className="assessment-grid">
            <AssessmentItem
              icon={ShieldAlert}
              label="DOCUMENT"
              value={hashCalculated ? "FILE CHECKED" : "UNCONFIRMED"}
              state={hashCalculated ? "complete" : "pending"}
            />

            <AssessmentItem
              icon={Fingerprint}
              label="IDENTITY"
              value="NOT VERIFIED"
              state="pending"
            />

            <AssessmentItem
              icon={ScanSearch}
              label="FORENSICS"
              value="LIMITED CHECKS"
              state="pending"
            />

            <AssessmentItem
              icon={Sparkles}
              label="SYNTHETIC"
              value="MODEL UNAVAILABLE"
              state="pending"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

function AssessmentItem({ icon: Icon, label, value, state }) {
  return (
    <div className="assessment-item">
      <div className={`assessment-icon ${state}`}>
        <Icon size={13} strokeWidth={2} />
      </div>

      <div className="assessment-copy">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function formatTime(timestamp) {
  if (!timestamp) return "--:--";

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return "--:--";
  }

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default CaseOverview;