import os
import sys
import tempfile
from pathlib import Path

# Cấu hình môi trường ghi tạm cho các thư viện Python trên serverless
TEMP_BASE = tempfile.gettempdir()
os.environ["MPLCONFIGDIR"] = os.path.join(TEMP_BASE, "matplotlib")
os.environ["HOME"] = TEMP_BASE

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server import app
