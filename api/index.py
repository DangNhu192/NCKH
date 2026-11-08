import os
import sys
import tempfile
from pathlib import Path

# Cấu hình môi trường ghi tạm cho các thư viện Python trên serverless
TEMP_BASE = tempfile.gettempdir()
os.environ["MPLCONFIGDIR"] = os.path.join(TEMP_BASE, "matplotlib")
os.environ["HOME"] = TEMP_BASE

# Thêm project root directory vào sys.path để server và các modules có thể import chính xác
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from server import app
except Exception as e:
    import traceback
    err_tb = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    app = FastAPI(title="Web Super Startup Error")

    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
    def error_handler(path_name: str = ""):
        return HTMLResponse(
            f"<h2>Khởi động Web Super trên Vercel gặp lỗi:</h2><pre>{err_tb}</pre>",
            status_code=500
        )
