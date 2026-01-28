import tomllib
from pathlib import Path
from utils import get_config_path

class Config:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.toml"
        with open(config_path, "rb") as f:
            self.config = tomllib.load(f)

    @property
    def server_domain(self):
        return self.config.get("server", {}).get("server_domain", "")

    @property
    def poll_interval_seconds(self):
        return self.config.get("client", {}).get("poll_iterval_seconds", 5)

    @property
    def db_name(self):
        return self.config.get("db" , {}).get("db_name", "gop.db")
    
config = Config(get_config_path())
