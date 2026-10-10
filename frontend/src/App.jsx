import "./App.css";
import { useEffect, useState } from "react";
import { Activity, RefreshCw } from "lucide-react";

import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";
import CaseOverview from "./components/CaseOverview";
import AnalysisPipeline from "./components/AnalysisPipeline";
import InvestigationTimeline from "./components/InvestigationTimeline";
import SystemStatus from "./components/SystemStatus";
import EvidenceUpload from "./components/EvidenceUpload";
import CaseManagement from "./components/CaseManagement";


const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

function App() {

  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [loading, setLoading] = useState(true);
  const [backendOnline, setBackendOnline] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const [activeView, setActiveView] = useState("Command");


  async function loadCases() {

    setLoading(true);

    try {

      const response = await fetch(
        `${API_BASE}/api/v1/cases`
      );

      if (!response.ok) {
        throw new Error(
          "Unable to reach SENTINEL API"
        );
      }

      const data = await response.json();

      setCases(data.cases || []);
      setBackendOnline(true);


      if (data.cases?.length > 0) {

        const latestCase = data.cases[0];

        const detailResponse = await fetch(
          `${API_BASE}/api/v1/cases/${latestCase.case_id}`
        );

        if (detailResponse.ok) {

          const detail =
            await detailResponse.json();

          setSelectedCase(detail);

        } else {

          setSelectedCase(latestCase);

        }

      } else {

        setSelectedCase(null);

      }

    } catch (error) {

      console.error(
        "SENTINEL API:",
        error
      );

      setBackendOnline(false);
      setSelectedCase(null);

    } finally {

      setLoading(false);

    }

  }


  async function openCase(caseId) {

    try {

      const response = await fetch(
        `${API_BASE}/api/v1/cases/${caseId}`
      );

      if (!response.ok) {

        throw new Error(
          "Unable to open case."
        );

      }

      const caseData =
        await response.json();

      setSelectedCase(caseData);

      setActiveView("Command");

    } catch (error) {

      console.error(
        "SENTINEL CASE:",
        error
      );

    }

  }


  useEffect(() => {

    loadCases();

  }, []);


  async function handleCaseCreated() {

    await loadCases();

    setActiveView("Command");

  }


  function handleNavigation(label) {

    setActiveView(label);

    setMobileOpen(false);

  }


  return (

    <div className="sentinel-app">

      <Sidebar
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
        activeView={activeView}
        onNavigate={handleNavigation}
      />


      <main className="main-shell">

        <TopBar
          setMobileOpen={setMobileOpen}
        />


        <div className="command-content">


          {activeView === "Cases" ? (

            <CaseManagement
              cases={cases}
              loading={loading}
              onOpenCase={openCase}
            />

          ) : (

            <CommandCenter
              cases={cases}
              selectedCase={selectedCase}
              backendOnline={backendOnline}
              loading={loading}
              loadCases={loadCases}
              handleCaseCreated={handleCaseCreated}
            />

          )}


        </div>

      </main>

    </div>

  );

}


function CommandCenter({
  cases,
  selectedCase,
  backendOnline,
  loading,
  loadCases,
  handleCaseCreated,
}) {

  return (

    <>

      <section className="command-intro">

        <div>

          <div className="intro-overline">
            SENTINEL OPERATIONS // 08 OCT 2026
          </div>


          <h1>
            Digital Identity
            <span>
              Intelligence Center
            </span>
          </h1>


          <p>
            Multimodal evidence analysis and synthetic media
            security environment.
          </p>

        </div>


        <div className="intro-status">

          <div className="intro-status-icon">
            <Activity size={16} />
          </div>


          <div>

            <span>
              NETWORK STATUS
            </span>

            <strong>
              {backendOnline
                ? "OPERATIONAL"
                : "OFFLINE"}
            </strong>

          </div>

        </div>

      </section>


      <section className="command-metrics">

        <Metric
          label="ACTIVE CASES"
          value={cases.length
            .toString()
            .padStart(2, "0")}
          detail="REGISTERED INVESTIGATIONS"
        />


        <Metric
          label="CURRENT RISK"
          value={
            selectedCase
              ? Number(
                  selectedCase.risk_score
                ).toFixed(2)
              : "--.--"
          }
          detail={
            selectedCase
              ? `${selectedCase.risk_level} THREAT LEVEL`
              : "NO ACTIVE CASE"
          }
        />


        <Metric
          label="ANALYSIS STATE"
          value={
            selectedCase
              ? "01"
              : "00"
          }
          detail={
            selectedCase
              ? "CASE IN PIPELINE"
              : "AWAITING EVIDENCE"
          }
        />


        <Metric
          label="CORE STATUS"
          value={
            backendOnline
              ? "ON"
              : "OFF"
          }
          detail={
            backendOnline
              ? "FASTAPI NODE ACTIVE"
              : "NODE UNAVAILABLE"
          }
        />


        <button
          className="refresh-button"
          onClick={loadCases}
          disabled={loading}
          title="Refresh system data"
        >

          <RefreshCw
            size={16}
            className={
              loading
                ? "spin"
                : ""
            }
          />

          <span>
            SYNC
          </span>

        </button>

      </section>


      <EvidenceUpload
        onCaseCreated={handleCaseCreated}
      />


      <CaseOverview
        caseData={selectedCase}
      />


      <AnalysisPipeline />


      <InvestigationTimeline />


      <SystemStatus />


      <footer className="command-footer">

        <div>

          <span>
            SENTINEL-ID
          </span>

          <span>
            AI-POWERED MULTIMODAL DIGITAL IDENTITY SECURITY
          </span>

        </div>


        <div>

          <span>
            BUILD 0.1.0
          </span>

          <span>
            LOCAL NODE
          </span>

          <span>
            © 2026
          </span>

        </div>

      </footer>

    </>

  );

}


function Metric({
  label,
  value,
  detail
}) {

  return (

    <div className="metric">

      <span className="metric-label">
        {label}
      </span>

      <strong>
        {value}
      </strong>

      <span className="metric-detail">
        {detail}
      </span>

    </div>

  );

}


export default App;