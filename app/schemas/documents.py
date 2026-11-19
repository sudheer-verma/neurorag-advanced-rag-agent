from pydantic import BaseModel, Field
from typing import List


class IngestRequest(BaseModel):
    text: str = Field(min_length=1)
    title: str = "Untitled document"
    metadata: dict = {}


class DocumentRecord(BaseModel):
    id: str
    title: str
    status: str
    chunk_count: int
    metadata: dict = {}
