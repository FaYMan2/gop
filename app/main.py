from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.models import Item, ItemType
from app.db import init_db, test_db, get_connection

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
    return {"message": "Welcome to LocalSync API","tables" : rows}


@app.post("/add-item")
async def add_item(item : Item):
    conn = get_connection()
    

# For running directly with: python -m app.main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
