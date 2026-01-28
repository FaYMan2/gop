from pathlib import Path
import platform
import os

def get_config_path():
    if platform.system() == "Windows":
        base = Path(os.getenv("APPDATA") or  "")
    else:
        base = Path.home()

    return base / ".gop" / "config.toml"
