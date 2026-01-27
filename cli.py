import typer
import requests
import os
import uuid
from pathlib import Path
import pyperclip
import platform

app = typer.Typer()
SERVER = "http://127.0.0.1:8000"

def get_device_name():
    try:
        return platform.node()
    except AttributeError:
        return os.environ.get("COMPUTERNAME", "unknown-device")

@app.command()
def add(
    value: str,
    type: str = typer.Option(..., "--type", "-t", help="file or text"),
    device: str = typer.Option(get_device_name(), "--device")
):
    """
    Add an item as file or text.
    """
    item_type = type.lower()

    if item_type == "file":
        file_path = Path(value).expanduser()
        if not file_path.exists():
            typer.echo(f"File not found: {value}")
            raise typer.Exit(1)

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        item = {
            "id": str(uuid.uuid4()),
            "device": device,
            "type": "file",
            "name": file_path.name,
            "path": str(file_path),
            "content": content,
        }

    elif item_type == "text":
        item = {
            "id": str(uuid.uuid4()),
            "device": device,
            "type": "text",
            "name": f"text-{uuid.uuid4().hex[:6]}",
            "content": value,
        }

    else:
        typer.echo("--type must be either 'file' or 'text'")
        raise typer.Exit(1)

    r = requests.post(f"{SERVER}/items", json=item)
    typer.echo(r.json())


@app.command()
def list():
    """List all items."""
    r = requests.get(f"{SERVER}/items")
    typer.echo(r.json())


@app.command()
def cs(
    push : bool = typer.Option(False, "--push", help="Push clipboard to sync server")
):
    """Send clipboard content to the server."""
    print("Clipboard sync:", "push" if push else "pull")
    if push:
        content = pyperclip.paste()

        if not content.strip():
            typer.echo("Clipboard is empty")
            raise typer.Exit(1)

        item = {
            "id": str(uuid.uuid4()),
            "device": get_device_name(),
            "type": "clipboard",
            "name": f"clipboard-{uuid.uuid4().hex[:6]}",
            "content": content,
        }

        typer.echo("Clipboard sent:" + str(item))
        r = requests.post(f"{SERVER}/items", json=item)
        typer.echo(r.json())
   
    else:
        r = requests.get(f"{SERVER}/clipboard")
        data = r.json()
        if data and 'content' in data and data['content'].strip():
            pyperclip.copy(data['content'])
            typer.echo("Clipboard updated.")
        else:
            typer.echo("No clipboard content available from server.")
            typer.echo("Clipboard received:" + str(data))

if __name__ == "__main__":
    app()