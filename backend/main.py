from fastapi import FastAPI

from backend.db.database import Base, engine
from backend.db import models


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SENTINEL-ID",
    description="AI-Powered Multimodal Digital Identity & Synthetic Media Security System",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "system": "SENTINEL-ID",
        "status": "online",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }