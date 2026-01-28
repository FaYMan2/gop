import websockets
import json 
import asyncio
import tomllib
from pathlib import Path
from utils import get_config_path, get_device_name

config_path = get_config_path()

if not Path(config_path).exists():
    raise FileNotFoundError(f'Config file not found at {config_path}')

f = open(config_path, "rb")
config = tomllib.load(f)
server_domain = config.get("server", {}).get("server_domain" , "")
poll_interval_seconds = config.get("client", {}).get("poll_interval_seconds", 5)
f.close()
ws_url = f"ws://{server_domain}/ws"
device_name = get_device_name()



