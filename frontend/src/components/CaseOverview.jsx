import {
  ArrowUpRight,
  Check,
  Clock3,
  FileImage,
  Fingerprint,
  ScanSearch,
  ShieldAlert,
  Sparkles,
} from "lucide-react";

function CaseOverview({ caseData }) {
  const fallbackCase = {
    case_id: "SNT-F939B9E4",
    filename: "signature me.jpg",
    file_type: "jpg",
    risk_level: "LOW",
    risk_score: 8.75,
    created_at: "2026-10-07T04:45:34.042022",
  };

  const currentCase = caseData || fallbackCase;

  const riskScore = Number(currentCase.risk_score || 0);
  const riskLevel = currentCase.risk_level || "LOW";

  return (
    <section className="case-overview">
      <div className="case-heading">
        <div>
          <div className="eyebrow-row">
            <span className="eyebrow">ACTIVE INVESTIGATION</span>
            <span className="case-live">
              <span />
              LIVE CASE
            </span>
          </div>

          <h1>{currentCase.case_id}</h1>

          <div className="case-meta">
            <span>{currentCase.filename}</span>
            <span className="meta-divider">/</span>
            <span>{String(currentCase.file_type).toUpperCase()}</span>
            <span className="meta-divider">/</span>
            <span>IDENTITY ANALYSIS</span>
          </div>
        </div>

        <button className="case-action">
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
                {String(currentCase.file_type).toUpperCase()} // SOURCE FILE
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

            <span>SHA-256 VERIFIED</span>
          </div>
        </div>

        <div className="risk-panel">
          <div className="panel-label">
            <span>THREAT ASSESSMENT</span>
            <ShieldAlert size={15} />
          </div>

          <div className="risk-display">
            <div className="risk-number">
              {riskScore.toFixed(2)}
            </div>

            <div className={`risk-level ${riskLevel.toLowerCase()}`}>
              <span />
              {riskLevel}
            </div>

            <p>
              Composite risk score generated from
              available evidence analysis modules.
            </p>
          </div>

          <div className="risk-scale">
            <div className="scale-track">
              <span
                className="scale-marker"
                style={{
                  left: `${Math.min(riskScore, 100)}%`,
                }}
              />
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
              icon={Check}
              label="DOCUMENT"
              value="VERIFIED"
              state="complete"
            />

            <AssessmentItem
              icon={Fingerprint}
              label="IDENTITY"
              value="PENDING"
              state="pending"
            />

            <AssessmentItem
              icon={ScanSearch}
              label="FORENSICS"
              value="PENDING"
              state="pending"
            />

            <AssessmentItem
              icon={Sparkles}
              label="SYNTHETIC"
              value="PENDING"
              state="pending"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

function AssessmentItem({
  icon: Icon,
  label,
  value,
  state,
}) {
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