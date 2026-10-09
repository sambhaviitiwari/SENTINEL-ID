import {
  Activity,
  Database,
  Cpu,
  Server,
  Zap,
} from "lucide-react";

const systems = [
  {
    name: "API CORE",
    value: "ONLINE",
    detail: "127.0.0.1:8000",
    icon: Server,
  },
  {
    name: "DATABASE",
    value: "ONLINE",
    detail: "SQLite / SENTINEL.DB",
    icon: Database,
  },
  {
    name: "AI ENGINE",
    value: "STANDBY",
    detail: "ANALYSIS QUEUED",
    icon: Cpu,
  },
];

function SystemStatus() {
  return (
    <section className="system-status">
      <div className="section-heading">
        <div>
          <span className="eyebrow">INFRASTRUCTURE</span>
          <h2>System Status</h2>
        </div>

        <div className="system-health">
          <Activity size={14} />
          <span>ALL SYSTEMS NOMINAL</span>
        </div>
      </div>

      <div className="status-grid">
        {systems.map(({ name, value, detail, icon: Icon }) => (
          <div className="status-card" key={name}>
            <div className="status-card-top">
              <div className="status-icon">
                <Icon size={17} strokeWidth={1.6} />
              </div>

              <span className={`status-badge ${value === "ONLINE" ? "online" : "standby"}`}>
                <span />
                {value}
              </span>
            </div>

            <div className="status-name">{name}</div>

            <div className="status-detail">{detail}</div>

            <div className="status-bar">
              <span
                style={{
                  width: value === "ONLINE" ? "94%" : "31%",
                }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="system-footnote">
        <Zap size={12} />
        <span>SECURITY PROTOCOL ACTIVE</span>
        <span className="footnote-line" />
        <span>LOCAL DEVELOPMENT NODE</span>
      </div>
    </section>
  );
}

export default SystemStatus;