import sys
from pathlib import Path

# Thêm project root directory vào sys.path để server và các modules có thể import chính xác
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server import app
