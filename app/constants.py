import os
from pathlib import Path
import platform
from app.config_reader import config

# Cross-platform database path
if platform.system() == "Windows":
    BASE = Path(os.environ.get("APPDATA", Path.home())) / ".gop"
else:
    # macOS and Linux
    BASE = Path.home() / ".gop"

BASE.mkdir(exist_ok=True)
DB_PATH = BASE / config.db_name

SERVER_NAME = config.server_domain