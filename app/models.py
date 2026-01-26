from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ItemType(str, Enum):
    file = "file"
    text = "text"
    clipboard_item = "clipboard"


class Item(BaseModel):
    id: str
    device: str
    type: ItemType
    name: str
    content: Optional[str] = None
    path: Optional[str] = None
    created_at: Optional[datetime] = None