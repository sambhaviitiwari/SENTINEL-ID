import {
  Check,
  CircleDot,
  FileCheck2,
  Fingerprint,
  ScanFace,
  ShieldCheck,
} from "lucide-react";

const stages = [
  {
    number: "01",
    label: "EVIDENCE INGESTION",
    detail: "SOURCE RECEIVED",
    state: "complete",
    icon: FileCheck2,
  },
  {
    number: "02",
    label: "DOCUMENT INTEGRITY",
    detail: "ANALYSIS COMPLETE",
    state: "complete",
    icon: ShieldCheck,
  },
  {
    number: "03",
    label: "IDENTITY ANALYSIS",
    detail: "MODULE INITIALIZED",
    state: "active",
    icon: Fingerprint,
  },
  {
    number: "04",
    label: "BIOMETRIC MATCH",
    detail: "AWAITING INPUT",
    state: "pending",
    icon: ScanFace,
  },
  {
    number: "05",
    label: "SYNTHETIC MEDIA",
    detail: "MODULE QUEUED",
    state: "pending",
    icon: CircleDot,
  },
];

function AnalysisPipeline() {
  return (
    <section className="pipeline-section">
      <div className="section-heading">
        <div>
          <span className="eyebrow">ANALYSIS ENGINE</span>
          <h2>Investigation Pipeline</h2>
        </div>

        <div className="pipeline-id">
          PROCESS <strong>7F-A91C</strong>
        </div>
      </div>

      <div className="pipeline">
        {stages.map((stage, index) => {
          const Icon = stage.icon;

          return (
            <div className="pipeline-stage" key={stage.number}>
              <div className={`pipeline-node ${stage.state}`}>
                {stage.state === "complete" ? (
                  <Check size={14} />
                ) : (
                  <Icon size={14} strokeWidth={1.7} />
                )}
              </div>

              <div className="pipeline-copy">
                <div className="pipeline-number">
                  {stage.number}
                </div>

                <div className="pipeline-label">
                  {stage.label}
                </div>

                <div className={`pipeline-detail ${stage.state}`}>
                  {stage.detail}
                </div>
              </div>

              {index < stages.length - 1 && (
                <div
                  className={`pipeline-connector ${
                    stage.state === "complete" ? "complete" : ""
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}

export default AnalysisPipeline;