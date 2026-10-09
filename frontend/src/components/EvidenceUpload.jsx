import { useState } from "react";
import {
  Upload,
  FileCheck,
  AlertCircle,
  Loader2,
} from "lucide-react";

const API_BASE = "http://127.0.0.1:8000";


function EvidenceUpload({ onCaseCreated }) {

  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");


  function handleFileChange(event) {

    const selectedFile =
      event.target.files?.[0];

    setMessage("");
    setError("");

    if (!selectedFile) {
      setFile(null);
      return;
    }

    setFile(selectedFile);

  }


  async function handleUpload() {

    if (!file) {

      setError(
        "Select an evidence file before initiating analysis."
      );

      return;
    }


    setUploading(true);
    setMessage("");
    setError("");


    const formData = new FormData();

    formData.append(
      "file",
      file
    );


    try {

      const response = await fetch(
        `${API_BASE}/api/v1/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Evidence analysis failed."
        );

      }


      setMessage(
        `CASE ${data.case_id} CREATED — ${data.risk_level} RISK`
      );


      setFile(null);


      if (onCaseCreated) {

        await onCaseCreated(
          data.case_id
        );

      }


    } catch (uploadError) {

      console.error(
        "SENTINEL evidence upload:",
        uploadError
      );


      setError(
        uploadError.message ||
        "Unable to communicate with SENTINEL API."
      );


    } finally {

      setUploading(false);

    }

  }


  return (

    <section className="evidence-upload-panel">

      <div className="panel-heading">

        <div>

          <span className="panel-overline">
            EVIDENCE INGESTION
          </span>


          <h2>
            New Verification Case
          </h2>


          <p>
            Submit identity evidence for multimodal
            security analysis.
          </p>

        </div>


        <Upload size={20} />

      </div>


      <label className="upload-zone">

        <input
          type="file"
          accept=".jpg,.jpeg,.png,.pdf,.webp"
          onChange={handleFileChange}
          hidden
        />


        {file ? (

          <>

            <FileCheck size={24} />


            <strong>
              {file.name}
            </strong>


            <span>
              {(file.size / 1024).toFixed(1)} KB
            </span>

          </>

        ) : (

          <>

            <Upload size={24} />


            <strong>
              SELECT EVIDENCE FILE
            </strong>


            <span>
              JPG · JPEG · PNG · PDF · WEBP
            </span>

          </>

        )}

      </label>


      <button
        className="evidence-submit"
        onClick={handleUpload}
        disabled={
          uploading ||
          !file
        }
      >

        {uploading ? (

          <>

            <Loader2
              className="spin"
              size={16}
            />

            ANALYZING EVIDENCE

          </>

        ) : (

          <>

            <Upload size={16} />

            INITIATE VERIFICATION

          </>

        )}

      </button>


      {message && (

        <div className="upload-message success">

          <FileCheck size={16} />

          <span>
            {message}
          </span>

        </div>

      )}


      {error && (

        <div className="upload-message error">

          <AlertCircle size={16} />

          <span>
            {error}
          </span>

        </div>

      )}

    </section>

  );

}


export default EvidenceUpload;