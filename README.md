# SENTINEL-ID

### AI-Powered Multimodal Digital Identity & Synthetic Media Security System

SENTINEL-ID is a security-focused web application for inspecting digital evidence and organizing investigations. It combines a React command-center interface with a FastAPI backend and a SQLite development database.

**Project status:** Active prototype and portfolio capstone.

The current application includes a security dashboard, evidence-analysis workflow, case registry, document metadata inspection, and structured investigation records. Advanced biometric verification and synthetic-media detection require further implementation and validation before they can be considered production-ready.

---

## Project Overview

SENTINEL-ID aims to provide a unified workspace for examining digital evidence, recording investigation results, and organizing potential identity-security concerns.

### Current Features

- Dark, cyber-inspired command-center dashboard
- Evidence upload and analysis workflow
- Investigation case registry and case-detail views
- Document Intelligence metadata panel
- SHA-256 file fingerprinting when available
- File format and structural metadata inspection
- Backend API and database status monitoring
- Structured findings and risk assessment output
- PDF investigation report generation
- Interactive API documentation through FastAPI

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| UI | CSS, Lucide React |
| Backend | Python, FastAPI |
| Data validation | Pydantic |
| Database | SQLAlchemy, SQLite |
| Document inspection | Python imaging and document-processing libraries |
| Reporting | ReportLab |

## Application Architecture

```text
                  USER
                   |
                   v
          React + Vite Frontend
                   |
             HTTP / JSON
                   |
                   v
             FastAPI Backend
                   |
          Evidence Analysis Pipeline
                   |
          +--------+---------+
          |                  |
          v                  v
    Analysis Modules    Case Management
          |                  |
          +--------+---------+
                   |
                   v
           SQLAlchemy + SQLite
                   |
                   v
          Investigation Records
```

## Project Structure

```text
SENTINEL-ID/
├── backend/
│   ├── api/
│   ├── core/
│   ├── db/
│   └── modules/
├── frontend/
│   ├── src/
│   │   └── components/
│   ├── package.json
│   └── vite.config.js
├── requirements.txt
├── .gitignore
└── README.md
```

## Run the Project Locally

### Prerequisites

- Python 3.11 or a compatible version
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/sambhaviitiwari/SENTINEL-ID.git
cd SENTINEL-ID
```

### 2. Start the backend

From the repository root, create and activate a virtual environment:

**Windows CMD**

```cmd
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001
```

The backend should be available at:

- API root: `http://127.0.0.1:8001/`
- System status: `http://127.0.0.1:8001/status`
- Interactive API documentation: `http://127.0.0.1:8001/docs`

Keep this terminal running.

### 3. Start the frontend

Open a second CMD window:

```cmd
cd /d "C:\Users\sambh\OneDrive\Desktop\SENTINEL-ID\frontend"
npm install
npm run dev
```

Open the local address printed by Vite, normally:

`http://localhost:5173`

### 4. Build the frontend

From the `frontend` directory:

```cmd
npm run build
```

Vite writes the production build to `frontend/dist/`.

## API Overview

The backend currently exposes endpoints for system status, evidence analysis, and case management.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/status` | System and service status |
| POST | `/api/v1/analyze` | Submit evidence for analysis |
| GET | `/api/v1/cases` | List registered cases |
| GET | `/api/v1/cases/{case_id}` | Retrieve a case |

Visit `/docs` on the running backend to inspect the available request schemas and responses.

## Development Status

### Implemented or checked locally

- [x] React dashboard and navigation
- [x] FastAPI backend foundation
- [x] Database integration
- [x] Case registry and case-detail workflow
- [x] Document metadata interface
- [x] Evidence-analysis pipeline foundation
- [x] Frontend production build
- [x] Local API status check

### Remaining work

- [ ] Automated end-to-end and regression tests
- [ ] Comprehensive upload and report-generation validation
- [ ] Evaluation of biometric and synthetic-media analysis models
- [ ] Authentication and authorization
- [ ] Secure evidence storage and retention controls
- [ ] Production deployment
- [ ] Public demo and application screenshots
- [ ] Deployment and security documentation

This checklist reflects development progress, not independent certification or production readiness.

## Security and Limitations

SENTINEL-ID is an experimental prototype, not a certified forensic or identity-verification service.

- A SHA-256 hash identifies file contents; it does not establish that a document is authentic.
- Metadata and structural checks can provide useful signals but cannot independently prove fraud.
- Risk classifications should be interpreted alongside the findings and limitations of the analysis.
- Biometric and synthetic-media detection capabilities must be evaluated before being relied on for real decisions.
- Use synthetic or non-sensitive sample evidence for demonstrations.
- Do not upload real identity documents or confidential investigation data to a public demo.

Before production deployment, the application requires appropriate access controls, upload validation and size limits, safe file storage, rate limiting, restricted CORS origins, and a defined data-retention policy.

## Roadmap

- [x] Establish the full-stack application foundation
- [x] Build the command-center interface
- [x] Integrate case management and document inspection
- [ ] Strengthen automated testing and error handling
- [ ] Validate individual analysis modules
- [ ] Complete the public deployment
- [ ] Publish genuine application screenshots
- [ ] Document the live demo and deployment architecture

## Author

Developed as a software engineering and digital-security portfolio project.

**Repository:** [SENTINEL-ID](https://github.com/sambhaviitiwari/SENTINEL-ID)

## License

No license has been selected yet. Until a license is added, others should not assume they have permission to reuse, modify, or redistribute this code.
