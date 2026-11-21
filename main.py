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


def _create_app() -> FastAPI:
    """Nạp ứng dụng chính; nếu lỗi khởi động thì trả về app chẩn đoán hiển thị traceback."""
    global init_error
    try:
        from server import app as real_app
        return real_app
    except Exception as e:
        init_error = "".join(traceback.format_exception(type(e), e, e.__traceback__))

    debug_app = FastAPI(title="Web Super Startup Debug")
    debug_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return debug_app


# Vercel tìm biến "app" ở cấp ngoài cùng của main.py (không nằm trong try/if)
app = _create_app()

# Add debug startup endpoint
@app.get("/api/debug-startup")
def debug_startup():
    warnings = []
    try:
        from modules.auth import auth_service
        if auth_service.JWT_SECRET_WARNING:
            warnings.append(auth_service.JWT_SECRET_WARNING)
    except Exception:
        pass
    if os.getenv("VERCEL") and not (os.getenv("VAULT_MASTER_SECRET") and os.getenv("VAULT_MASTER_SALT")):
        warnings.append("Chưa đặt VAULT_MASTER_SECRET / VAULT_MASTER_SALT: API key người dùng được mã hóa bằng khóa tạm thời.")
    return {
        "security_warnings": warnings,
        "status": "ok" if init_error is None else "error",
        "service": "WEB SUPER v2.0",
        "has_init_error": init_error is not None,
        "error_details": init_error
    }


if init_error is not None:
    # Đăng ký sau /api/debug-startup để route chẩn đoán không bị che
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
