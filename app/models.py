from pydantic import BaseModel
from enum import Enum


class ItemType(Enum):
    file = "file"
    text = "text"
    clipboard_item = "clipboard_item"
    

class Item(BaseModel):
    item_name : str
    item_type : ItemType
    device_name : str