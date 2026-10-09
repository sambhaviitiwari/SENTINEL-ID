import {
  Archive,
  BarChart3,
  FileSearch,
  Fingerprint,
  FolderOpen,
  LayoutDashboard,
  ScanFace,
  Shield,
  Terminal,
  X,
} from "lucide-react";


const navigation = [
  { label: "Command", icon: LayoutDashboard },
  { label: "Cases", icon: FolderOpen },
  { label: "Evidence", icon: Archive },
  { label: "Identity", icon: Fingerprint },
  { label: "Forensics", icon: FileSearch },
  { label: "Synthetic", icon: ScanFace },
  { label: "Reports", icon: BarChart3 },
];


function Sidebar({
  mobileOpen,
  setMobileOpen,
  activeView,
  onNavigate,
}) {

  return (

    <>

      <div
        className={`sidebar-overlay ${
          mobileOpen ? "visible" : ""
        }`}
        onClick={() => setMobileOpen(false)}
      />


      <aside
        className={`sidebar ${
          mobileOpen ? "mobile-open" : ""
        }`}
      >

        <div className="sidebar-header">

          <div className="brand-mark">
            <Shield
              size={19}
              strokeWidth={1.7}
            />
          </div>


          <div className="brand-copy">

            <span className="brand-name">
              SENTINEL
            </span>

            <span className="brand-id">
              ID // 01
            </span>

          </div>


          <button
            className="mobile-close"
            onClick={() =>
              setMobileOpen(false)
            }
            aria-label="Close navigation"
          >

            <X size={18} />

          </button>

        </div>


        <div className="classification">

          <span className="classification-dot" />

          <span>
            SECURE ENVIRONMENT
          </span>

          <span className="classification-level">
            LVL 04
          </span>

        </div>


        <nav className="navigation">

          <div className="nav-section-label">
            COMMAND
          </div>


          {navigation.map(
            ({ label, icon: Icon }) => {

              const isActive =
                activeView === label;

              return (

                <button
                  key={label}
                  className={`nav-item ${
                    isActive
                      ? "active"
                      : ""
                  }`}
                  onClick={() =>
                    onNavigate(label)
                  }
                >

                  <Icon
                    size={17}
                    strokeWidth={1.65}
                  />

                  <span>
                    {label}
                  </span>


                  {isActive && (
                    <span className="nav-active-line" />
                  )}

                </button>

              );

            }
          )}

        </nav>


        <div className="sidebar-spacer" />


        <div className="system-section">

          <div className="nav-section-label">
            SYSTEM
          </div>


          <div className="system-item">

            <span className="status-light online" />

            <span>
              API CORE
            </span>

            <span className="system-state">
              ONLINE
            </span>

          </div>


          <div className="system-item">

            <span className="status-light online" />

            <span>
              DATABASE
            </span>

            <span className="system-state">
              ONLINE
            </span>

          </div>


          <div className="system-item">

            <span className="status-light pending" />

            <span>
              AI ENGINE
            </span>

            <span className="system-state">
              STANDBY
            </span>

          </div>

        </div>


        <div className="sidebar-footer">

          <div className="terminal-icon">
            <Terminal size={14} />
          </div>


          <div>

            <span className="footer-label">
              SENTINEL CORE
            </span>

            <span className="footer-version">
              BUILD 0.1.0 // LOCAL
            </span>

          </div>

        </div>

      </aside>

    </>

  );

}


export default Sidebar;