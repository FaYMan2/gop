from websockets.asyncio.client import connect
import json
import asyncio
import tomllib
from pathlib import Path
import hashlib
import pyperclip

from utils import get_config_path, get_device_name

config_path = get_config_path()

if not Path(config_path).exists():
    raise FileNotFoundError(f"Config file not found at {config_path}")

with open(config_path, "rb") as f:
    config = tomllib.load(f)

server_domain = config.get("server", {}).get("server_domain", "")
poll_interval_seconds = config.get("client", {}).get("poll_interval_seconds", 5)
server_port = config.get("server", {}).get("port", 8000)
ws_url = f"ws://{server_domain}.local:{server_port}/live"
device_name = get_device_name()

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

async def main():
    last_local_hash = None
    last_remote_hash = None
    async with connect(ws_url) as websocket:
        print(f"Connected to {ws_url} as {device_name}")

        async def poll_clipboard():
            nonlocal last_local_hash

            while True:
                try:
                    text = pyperclip.paste()
                    h = hash_text(text)
                    if h != last_local_hash:
                        payload = {
                            "type": "clipboard",
                            "device": device_name,
                            "content": text,
                            "hash": h,
                        }
                        await websocket.send(json.dumps(payload))
                        last_local_hash = h

                    await asyncio.sleep(poll_interval_seconds)

                except Exception as e:
                    print("Clipboard poll error:", e)
                    await asyncio.sleep(1)

        async def receive_updates():
            nonlocal last_remote_hash, last_local_hash

            async for msg in websocket:
                data = json.loads(msg)

                if data.get("event") != "clipboard_update":
                    continue

                content = data.get("content", "")
                h = hash_text(content)

                if h == last_local_hash:
                    continue

                if h == last_remote_hash:
                    continue

                pyperclip.copy(content)
                last_remote_hash = h

        await asyncio.gather(
            poll_clipboard(),
            receive_updates(),
        )


if __name__ == "__main__":
    asyncio.run(main())
