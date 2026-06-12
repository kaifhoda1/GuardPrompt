import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.proxy_routes import router as proxy_router
from config import APP_NAME, APP_VERSION
from storage.database import init_db

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Real-time prompt injection detection middleware"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(proxy_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"status": "GuardPrompt is running", "version": APP_VERSION}

@app.get("/health")
def health():
    return {"status": "ok"}
