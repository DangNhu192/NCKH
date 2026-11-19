import os
import sys
import tempfile
import traceback
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

TEMP_BASE = tempfile.gettempdir()
os.environ["MPLCONFIGDIR"] = os.path.join(TEMP_BASE, "matplotlib")
os.environ["HOME"] = TEMP_BASE
os.environ["VERCEL"] = "1"

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

init_error = None
try:
    from server import app as real_app
    app = real_app
except Exception as e:
    init_error = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    app = FastAPI(title="Web Super Startup Debug")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
    def error_route(path_name: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Startup Exception in main.py",
                "path": path_name,
                "traceback": init_error
            }
        )

# Add debug startup endpoint
@app.get("/api/debug-startup")
def debug_startup():
    return {
        "status": "ok" if init_error is None else "error",
        "service": "WEB SUPER v2.0",
        "has_init_error": init_error is not None,
        "error_details": init_error
    }
