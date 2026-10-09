import { Clock3, ShieldCheck, ScanSearch, FileSearch, BrainCircuit } from "lucide-react";

const timelineEvents = [
  {
    time: "SYSTEM",
    title: "SENTINEL CORE INITIALIZED",
    description: "Local intelligence environment established.",
    icon: ShieldCheck,
    state: "COMPLETE",
  },
  {
    time: "01",
    title: "IDENTITY EVIDENCE INGESTION",
    description: "Multimodal evidence prepared for analysis.",
    icon: FileSearch,
    state: "READY",
  },
  {
    time: "02",
    title: "FORENSIC ANALYSIS",
    description: "Identity and media consistency checks queued.",
    icon: ScanSearch,
    state: "STANDBY",
  },
  {
    time: "03",
    title: "AI RISK ASSESSMENT",
    description: "Synthetic media and identity risk evaluation.",
    icon: BrainCircuit,
    state: "STANDBY",
  },
];

function InvestigationTimeline() {
  return (
    <section className="investigation-timeline">
      <div className="section-heading">
        <div>
          <span className="section-kicker">INVESTIGATION LOG</span>
          <h2>Investigation Timeline</h2>
        </div>

        <div className="section-status">
          <Clock3 size={15} />
          <span>LIVE</span>
        </div>
      </div>

      <div className="timeline">
        {timelineEvents.map((event, index) => {
          const Icon = event.icon;

          return (
            <div className="timeline-item" key={event.title}>
              <div className="timeline-marker">
                <Icon size={15} />
              </div>

              {index < timelineEvents.length - 1 && (
                <div className="timeline-line" />
              )}

              <div className="timeline-content">
                <div className="timeline-meta">
                  <span>{event.time}</span>
                  <span>{event.state}</span>
                </div>

                <h3>{event.title}</h3>

                <p>{event.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export default InvestigationTimeline;