import {
  Bell,
  Menu,
  ShieldCheck,
  Wifi,
} from "lucide-react";

function TopBar({ setMobileOpen }) {
  return (
    <header className="topbar">
      <button
        className="mobile-menu"
        onClick={() => setMobileOpen(true)}
        aria-label="Open navigation"
      >
        <Menu size={21} />
      </button>

      <div className="topbar-context">
        <div className="context-kicker">
          <span className="live-pulse" />
          COMMAND CENTER
        </div>

        <span className="context-separator">/</span>

        <span className="context-page">OVERVIEW</span>
      </div>

      <div className="topbar-right">
        <div className="secure-channel">
          <ShieldCheck size={15} />
          <span>SECURE CHANNEL</span>
          <strong>04</strong>
        </div>

        <div className="topbar-divider" />

        <div className="network-status">
          <Wifi size={15} />
          <span>LOCAL</span>
        </div>

        <button className="notification-button" aria-label="Notifications">
          <Bell size={17} />
          <span className="notification-dot" />
        </button>

        <div className="operator">
          <div className="operator-avatar">S</div>

          <div className="operator-info">
            <span>OPERATOR</span>
            <strong>SENTINEL</strong>
          </div>
        </div>
      </div>
    </header>
  );
}

export default TopBar;
