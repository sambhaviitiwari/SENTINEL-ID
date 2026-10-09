
import {
  ArrowUpRight,
  Clock3,
  FileText,
  ShieldAlert,
} from "lucide-react";

function CaseManagement({ cases, loading, onOpenCase }) {
  return (
    <section className="case-management">
      <div className="case-management-header">
        <div>
          <div className="intro-overline">
            SENTINEL CASE REGISTRY
          </div>

          <h1>Case Management</h1>

          <p>
            Registered investigations and digital evidence records.
          </p>
        </div>

        <div className="case-count">
          <span>REGISTERED CASES</span>
          <strong>{String(cases.length).padStart(2, "0")}</strong>
        </div>
      </div>

      {loading ? (
        <div className="case-empty-state">
          <span>LOADING CASE REGISTRY...</span>
        </div>
      ) : cases.length === 0 ? (
        <div className="case-empty-state">
          <FileText size={24} />

          <strong>NO CASES REGISTERED</strong>

          <span>
            Submit evidence from the Command Center to create
            a verification case.
          </span>
        </div>
      ) : (
        <div className="case-list">
          {cases.map((caseItem) => {
            const findings = Array.isArray(caseItem.findings)
              ? caseItem.findings.join("\n").toLowerCase()
              : String(caseItem.findings || "").toLowerCase();

            const isCurrentAssessment = findings.includes(
              "overall risk classification is inconclusive"
            );

            const riskLevel = isCurrentAssessment
              ? caseItem.risk_level || "INCONCLUSIVE"
              : "INCONCLUSIVE";

            const score = Number(caseItem.risk_score);

            const hasValidScore =
              isCurrentAssessment &&
              caseItem.risk_score !== null &&
              caseItem.risk_score !== undefined &&
              caseItem.risk_score !== "" &&
              Number.isFinite(score);

            return (
              <article
                className="case-card"
                key={caseItem.case_id}
              >
                <div className="case-card-main">
                  <div className="case-card-icon">
                    <ShieldAlert size={18} />
                  </div>

                  <div className="case-card-identity">
                    <span className="case-card-label">
                      CASE ID
                    </span>

                    <h2>{caseItem.case_id}</h2>

                    <div className="case-card-file">
                      <FileText size={13} />

                      <span>{caseItem.filename}</span>

                      <span className="meta-divider">/</span>

                      <span>
                        {String(caseItem.file_type || "unknown").toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="case-card-risk">
                  <span className="case-card-label">
                    FILE CHECK SCORE
                  </span>

                  <strong>
                    {hasValidScore ? score.toFixed(2) : "—"}
                  </strong>

                  <span
                    className={`case-risk-badge ${riskLevel.toLowerCase()}`}
                  >
                    {riskLevel}
                  </span>

                  <small>
                    {hasValidScore
                      ? "Not an identity or deepfake risk score"
                      : "Legacy result; score not validated"}
                  </small>
                </div>

                <div className="case-card-time">
                  <span className="case-card-label">
                    CREATED
                  </span>

                  <span>
                    <Clock3 size={12} />
                    {formatDate(caseItem.created_at)}
                  </span>
                </div>

                <button
                  className="case-open-button"
                  onClick={() => onOpenCase(caseItem.case_id)}
                >
                  OPEN CASE
                  <ArrowUpRight size={15} />
                </button>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

function formatDate(timestamp) {
  if (!timestamp) return "--";

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) return "--";

  return date.toLocaleString([], {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default CaseManagement;
