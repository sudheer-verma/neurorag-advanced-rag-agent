from pydantic import BaseModel
from typing import Optional


class MemoryItem(BaseModel):
    id: int
    user_id: str
    fact: str
    category: str
    source_session: Optional[str] = None
