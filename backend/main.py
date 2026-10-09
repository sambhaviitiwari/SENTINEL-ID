from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.database import Base, engine
from backend.db import models
from backend.api.routes import router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SENTINEL-ID",
    description="AI-Powered Multimodal Digital Identity & Synthetic Media Security System",
    version="0.1.0"
)


# Allow React/Vite frontend to communicate with FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }