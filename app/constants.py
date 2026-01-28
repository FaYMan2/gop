import os
from pathlib import Path
import platform

# Cross-platform database path
if platform.system() == "Windows":
    BASE = Path(os.environ.get("APPDATA", Path.home())) / ".gop"
else:
    # macOS and Linux
    BASE = Path.home() / ".gop"

BASE.mkdir(exist_ok=True)
DB_PATH = BASE / "sync.db"

SERVER_NAME = "suvarna-local-sync"