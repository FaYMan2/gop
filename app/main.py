from typing import List

from fastapi import FastAPI

from app.models import Item, ItemType
from app.db import init_db, test_db, fetch_items, add_item, delete_item

# Initialize FastAPI app
app = FastAPI(
    title="LocalSync API",
    description="A local sync service with SQLite backend",
    version="1.0.0"
)

init_db()   

@app.get("/")
def root():
    rows = test_db()
    return {"message": "Welcome to Gop API","tables" : rows}

@app.get("/items", response_model=List[Item])
def get_items():
    return fetch_items()

@app.post("/items")
def add_item_endpoint(item: Item):
    return add_item(item)

@app.delete("/items/{item_id}")
def delete_item_endpoint(item_id: str | None):
    if item_id is None:
        return {"error": "Item ID is required"}
    return delete_item(item_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
