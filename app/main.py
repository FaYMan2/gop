from typing import List

from fastapi import FastAPI

from app.models import Item, ItemType
from app.db import db_service

# Initialize FastAPI app
app = FastAPI(
    title="LocalSync API",
    description="A local sync service with SQLite backend",
    version="1.0.0"
)

db_service.init_db()   

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
