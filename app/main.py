from typing import List

from fastapi import FastAPI, Request, HTTPException, status
from fastapi import websockets, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.models import Item, ItemType
from app.db import db_service
from app.mdns import register_service
from pathlib import Path
from app.socket import wsConnectionManager

templates = Jinja2Templates(directory="app/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    db_service.init_db()

    azc, info = await register_service()
    app.state.azc = azc
    app.state.zeroconf_info = info

    print(f"Service {info.name} registered, IP: {info.parsed_addresses()[0]}:{info.port}")
    yield

    print("Shutting down...")
    azc = app.state.azc
    await azc.async_unregister_all_services()
    await azc.async_close()


app = FastAPI(
    title="LocalSync API",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

connectionManager = wsConnectionManager()

# Web UI
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    items = db_service.fetch_items()
    return templates.TemplateResponse(
        name="items.html",
        context={"request": request, "items": items}
    )


# API Endpoints
@app.get("/items", response_model=List[Item], status_code=status.HTTP_200_OK)
def get_items():
    return db_service.fetch_items()


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def add_item_endpoint(item: Item):
    if item.type == ItemType.clipboard_item:
        return db_service.update_clipboard_item(item)

    return db_service.add_item(item)


@app.get("/clipboard", response_model=Item, status_code=status.HTTP_200_OK)
def get_clipboard_item():
    clipboard = db_service.fetch_clipboard_item()

    if not clipboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No clipboard item found"
        )

    return Item(**clipboard[0])


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_endpoint(item_id: str):
    if not item_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item ID is required"
        )

    deleted = db_service.delete_item(item_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    return None


@app.get("/download/{item_id}")
async def download_item(item_id: str):
    if not item_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item ID is required"
        )

    item = db_service.fetch_item_by_id(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    if item["type"] != ItemType.file:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Item is not a file"
        )

    file_path = Path(item["path"]).expanduser()

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="File no longer exists on source device"
        )

    return FileResponse(
        path=file_path,
        filename=item["name"],
        media_type="application/octet-stream"
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: websockets.WebSocket):
    await connectionManager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == ItemType.clipboard_item.value:
                db_service.update_clipboard_item(
                    Item(
                        id="clipboard",
                        device=data.get("device", "unknown"),
                        type=ItemType.clipboard_item,
                        name="clipboard",
                        content=data["content"]
                    )
                )
                await connectionManager.broadcast({
                    "event" : "clipboard_update",
                    "content" : data["content"]
                })
                
    except WebSocketDisconnect:
        connectionManager.disconnect(websocket)
            
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
