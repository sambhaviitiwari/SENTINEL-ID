import {
  Download,
  Clock3,
  FileImage,
  Fingerprint,
  ScanSearch,
  ShieldAlert,
  Sparkles,
  Hash,
  AlertTriangle,
  LoaderCircle,
} from "lucide-react";
import { useState } from "react";

const API_BASE = "http://127.0.0.1:8001";

function CaseOverview({ caseData }) {
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState("");

  const currentCase = caseData || {
    case_id: "NO CASE SELECTED",
    filename: "No evidence selected",
    file_type: "unknown",
    risk_level: "INCONCLUSIVE",
    risk_score: null,
    created_at: null,
    findings: [],
    analysis_details: null,
  };

  const analysis = currentCase.analysis_details || {};
  const documentAnalysis = analysis.document_analysis || {};
  const documentDetails = documentAnalysis.details || {};
  const faceAnalysis = analysis.face_analysis || {};
  const faceDetails = faceAnalysis.details || {};
  const identityAnalysis = analysis.identity_analysis || {};
  const syntheticAnalysis = analysis.synthetic_media_analysis || {};

  const findings = Array.isArray(currentCase.findings)
    ? currentCase.findings.join("\n").toLowerCase()
    : String(currentCase.findings || "").toLowerCase();

  const hasCurrentAssessment =
    findings.includes("overall risk classification is inconclusive") ||
    analysis.overall_risk === "INCONCLUSIVE";

  const riskLevel = hasCurrentAssessment
    ? "INCONCLUSIVE"
    : "INCONCLUSIVE";

  const rawDocumentScore = documentAnalysis.risk_score;
  const parsedDocumentScore = Number(rawDocumentScore);

  const hasDocumentScore =
    rawDocumentScore !== null &&
    rawDocumentScore !== undefined &&
    rawDocumentScore !== "" &&
    Number.isFinite(parsedDocumentScore);

  const scoreDisplay = hasDocumentScore
    ? parsedDocumentScore.toFixed(2)
    : "N/A";

  const hash =
    documentDetails.sha256 ||
    identityAnalysis.details?.sha256 ||
    "";

  const hashCalculated = Boolean(hash);

  const dimensions = documentDetails.image_dimensions;
  const imageDimensions =
    dimensions?.width && dimensions?.height
      ? String(dimensions.width) + ' x ' + String(dimensions.height)
      : 'N/A';

  const fileSize = Number(documentDetails.size_bytes);
  const fileSizeDisplay =
    Number.isFinite(fileSize) && fileSize >= 0
      ? formatFileSize(fileSize)
      : "N/A";

  const detectedFormat =
    documentDetails.image_format_detected ||
    documentDetails.file_extension ||
    currentCase.file_type ||
    "Unknown";

  const signatureStatus =
    documentDetails.signature_check || "Not available";

  const metadataStatus =
    documentDetails.metadata_inspection || "Not available";

  const exifStatus =
    documentDetails.exif_metadata_present === true
      ? "PRESENT"
      : documentDetails.exif_metadata_present === false
        ? "NOT PRESENT"
        : "NOT CHECKED";

  const authenticityStatus =
    documentDetails.authenticity_status || "not_verified";

  const faceDetectionStatus =
    faceDetails.face_detection_performed === true
      ? "PERFORMED"
      : faceDetails.face_detection_performed === false
        ? "NOT PERFORMED"
        : "NOT AVAILABLE";

  const syntheticModelStatus =
    syntheticAnalysis.details?.detection_model_available === true
      ? "AVAILABLE"
      : "UNAVAILABLE";

  async function downloadReport() {
    if (!caseData?.case_id || downloading) {
      return;
    }

    setDownloading(true);
    setDownloadError("");

    let objectUrl;

    try {
      const response = await fetch(
        API_BASE + '/api/v1/cases/' + encodeURIComponent(
          currentCase.case_id
        ) + '/report'
      );

      if (!response.ok) {
        throw new Error(
          'Report download failed with HTTP ' + response.status
        );
      }

      const contentType = response.headers.get("content-type") || "";

      if (
        !contentType.includes("application/pdf")
      ) {
        throw new Error("The server did not return a PDF file.");
      }

      const blob = await response.blob();
      objectUrl = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = currentCase.case_id + '-investigation-report.pdf';

      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Investigation report download failed:", error);

      setDownloadError(
        error.message ||
          "Unable to download the investigation report. Check the backend connection."
      );
    } finally {
      if (objectUrl) {
        window.setTimeout(() => {
          window.URL.revokeObjectURL(objectUrl);
        }, 1000);
      }

      setDownloading(false);
    }
  }

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

        <button
          className="case-action"
          type="button"
          onClick={downloadReport}
          disabled={!caseData?.case_id || downloading}
          title="Download the investigation report for this case"
        >
          {downloading ? (
            <>
              GENERATING REPORT
              <LoaderCircle className="download-spinner" size={15} />
            </>
          ) : (
            <>
              DOWNLOAD REPORT
              <Download size={15} />
            </>
          )}
        </button>
      </div>

      {downloadError && (
        <div className="document-disclaimer" role="alert">
          <AlertTriangle size={17} />
          <p>
            <strong>REPORT DOWNLOAD FAILED:</strong> {downloadError}
          </p>
        </div>
      )}

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
            <div className="risk-number">{riskLevel}</div>

            <div className={'risk-level ' + riskLevel.toLowerCase()}>
              <span />
              {riskLevel}
            </div>

            <p>
              The overall assessment is inconclusive. The document file-check
              score below reflects structural checks only, not verified
              identity authenticity or deepfake risk.
            </p>
          </div>

          <div className="risk-scale">
            <div className="scale-track" />

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
              value={
                documentAnalysis.status === "completed"
                  ? "STRUCTURE CHECKED"
                  : "LIMITED CHECKS"
              }
              state={
                documentAnalysis.status === "completed"
                  ? "complete"
                  : "pending"
              }
            />

            <AssessmentItem
              icon={Fingerprint}
              label="IDENTITY"
              value={
                identityAnalysis.details?.identity_verified === true
                  ? "VERIFIED"
                  : "NOT VERIFIED"
              }
              state="pending"
            />

            <AssessmentItem
              icon={ScanSearch}
              label="FORENSICS"
              value={
                faceDetails.face_detection_performed
                  ? "FACE CHECK PERFORMED"
                  : "LIMITED CHECKS"
              }
              state="pending"
            />

            <AssessmentItem
              icon={Sparkles}
              label="SYNTHETIC"
              value={
                syntheticAnalysis.details?.deepfake_detection_performed
                  ? "MODEL CHECK PERFORMED"
                  : "MODEL UNAVAILABLE"
              }
              state="pending"
            />
          </div>
        </div>
      </div>

      <section className="document-intelligence">
        <div className="section-heading">
          <div>
            <span className="eyebrow">EVIDENCE INSPECTION // 02</span>
            <h2>Document Intelligence</h2>
          </div>

          <div className="document-status">
            <span />
            {documentAnalysis.status === "completed"
              ? "INSPECTION COMPLETED"
              : "INSPECTION STATUS LIMITED"}
          </div>
        </div>

        <div className="document-metadata-grid">
          <MetadataItem
            label="FILE FORMAT"
            value={String(detectedFormat).toUpperCase()}
          />

          <MetadataItem
            label="FILE SIZE"
            value={fileSizeDisplay}
          />

          <MetadataItem
            label="IMAGE DIMENSIONS"
            value={imageDimensions}
          />

          <MetadataItem
            label="FILE SIGNATURE"
            value={String(signatureStatus).toUpperCase()}
          />

          <MetadataItem
            label="METADATA INSPECTION"
            value={String(metadataStatus).toUpperCase()}
          />

          <MetadataItem
            label="EXIF METADATA"
            value={exifStatus}
          />

          <MetadataItem
            label="AUTHENTICITY"
            value={String(authenticityStatus).replaceAll("_", " ").toUpperCase()}
          />

          <MetadataItem
            label="FILE CHECK SCORE"
            value={scoreDisplay}
          />
        </div>

        <div className="fingerprint-panel">
          <div className="fingerprint-heading">
            <div className="fingerprint-icon">
              <Hash size={17} />
            </div>

            <div>
              <span>CRYPTOGRAPHIC EVIDENCE IDENTIFIER</span>
              <strong>SHA-256 FINGERPRINT</strong>
            </div>

            <span
              className={`fingerprint-badge ${
                hashCalculated ? "available" : ""
              }`}
            >
              {hashCalculated ? "CALCULATED" : "UNAVAILABLE"}
            </span>
          </div>

          <div className="fingerprint-value">
            {hashCalculated ? hash : "No SHA-256 fingerprint available"}
          </div>

          <p>
            This hash identifies the file contents used during analysis.
            Matching hashes can help establish that two files are byte-for-byte
            identical; a hash alone does not establish that a document is
            genuine.
          </p>
        </div>

        <div className="document-metadata-grid secondary-metadata">
          <MetadataItem
            label="FACE DETECTION"
            value={faceDetectionStatus}
          />

          <MetadataItem
            label="SYNTHETIC DETECTION MODEL"
            value={syntheticModelStatus}
          />

          <MetadataItem
            label="IDENTITY VERIFICATION"
            value={
              identityAnalysis.details?.identity_verified === true
                ? "VERIFIED"
                : "NOT VERIFIED"
            }
          />

          <MetadataItem
            label="STRUCTURAL VALIDATION"
            value={String(
              documentDetails.structural_validation || "Not available"
            ).toUpperCase()}
          />
        </div>

        <div className="document-disclaimer">
          <AlertTriangle size={17} />

          <p>
            <strong>ANALYSIS LIMITATION:</strong> A passed file-signature or
            structural check does not prove that a document is authentic.
            Identity verification and synthetic-media detection are not
            confirmed unless their dedicated analysis models actually run and
            produce validated results. The overall case remains inconclusive.
          </p>
        </div>
      </section>
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

function MetadataItem({ label, value }) {
  return (
    <div className="document-metadata-item">
      <span>{label}</span>
      <strong>{value || "N/A"}</strong>
    </div>
  );
}

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatTime(timestamp) {
  if (!timestamp) return "--:--";

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) return "--:--";

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default CaseOverview;
