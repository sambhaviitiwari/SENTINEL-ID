
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.database import (
    Base,
    engine,
    migrate_case_analysis_details,
)
from backend.db import models
from backend.api.routes import router


Base.metadata.create_all(bind=engine)
migrate_case_analysis_details()


app = FastAPI(
    title="SENTINEL-ID",
    description="AI-Powered Multimodal Digital Identity & Synthetic Media Security System",
    version="0.1.0",
)


allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

frontend_origin = os.getenv("FRONTEND_ORIGIN", "").strip().rstrip("/")

if frontend_origin:
    allowed_origins.append(frontend_origin)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "system": "SENTINEL-ID",
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
