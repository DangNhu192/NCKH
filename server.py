# server.py
"""
WEB SUPER v2.0 - Unified AI Academic Research & Publishing Suite
Modular Architecture: Separate feature modules for each tab and functional area.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

# Load environment variables
load_dotenv()

# Setup base paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastAPI application
app = FastAPI(
    title="WEB SUPER v2.0",
    description="Hệ thống nghiên cứu khoa học & xuất bản học thuật tích hợp AI toàn diện",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IMPORT & REGISTER FEATURE ROUTERS (TỪNG MODULE CHỨC NĂNG) ---

from modules.auth.auth_router import auth_router
from modules.pipeline.pipeline_router import pipeline_router
from modules.harvester.harvester_router import harvester_router
from modules.notebooklm.notebooklm_router import notebooklm_router
from modules.zotero.zotero_router import zotero_router
from modules.academic_writer.writer_router import writer_router
from modules.editorial_office.editorial_router import editorial_router
from modules.humanizer.humanizer_router import humanizer_router
from modules.history.history_router import history_router
from modules.workspace.workspace_router import workspace_router
from modules.agency.agency_router import agency_router
from modules.admin_needle.admin_router import admin_router
from modules.math_chem_pro.math_chem_router import math_chem_router
from modules.bigquery.bigquery_router import bigquery_router

# Mount all feature routers
app.include_router(auth_router)
app.include_router(pipeline_router)
app.include_router(harvester_router)
app.include_router(notebooklm_router)
app.include_router(zotero_router)
app.include_router(writer_router)
app.include_router(editorial_router)
app.include_router(humanizer_router)
app.include_router(history_router)
app.include_router(workspace_router)
app.include_router(agency_router)
app.include_router(admin_router)
app.include_router(math_chem_router)
app.include_router(bigquery_router)

# --- SYSTEM HEALTH & ROOT STATIC SPA ---

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "WEB SUPER v2.0", "architecture": "Modular Feature-Driven"}

WORKSPACE_PATH = BASE_DIR / "workspace"
WORKSPACE_PATH.mkdir(parents=True, exist_ok=True)
app.mount("/workspace", StaticFiles(directory=str(WORKSPACE_PATH)), name="workspace")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>Web Super server running. static/index.html loading...</h1>")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8080"))
    print(f"🚀 WEB SUPER Modular Server đang khởi động tại: http://{host}:{port}")
    uvicorn.run("server:app", host=host, port=port, reload=False, access_log=True)
