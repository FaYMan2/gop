from typing import List

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models import Item, ItemType
from app.db import db_service
from app.mdns import register_service

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app : FastAPI):
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
    description="A local sync service with SQLite backend",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def root():
    rows = db_service.test_db()
    return {"message": "Welcome to Gop API","tables" : rows}

@app.get("/items", response_model=List[Item])
def get_items():
    return db_service.fetch_items()

@app.post("/items")
def add_item_endpoint(item: Item):
    if item.type == ItemType.clipboard_item:
        return db_service.update_clipboard_item(item)
    return db_service.add_item(item)

@app.get("/clipboard", response_model=Item | None)
def get_clipboard_item():
    clipboard = db_service.fetch_clipboard_item()
    if clipboard:
        return Item(**clipboard[0])
    return None

@app.delete("/items/{item_id}")
def delete_item_endpoint(item_id: str | None):
    if item_id is None:
        return {"error": "Item ID is required"}
    return db_service.delete_item(item_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
