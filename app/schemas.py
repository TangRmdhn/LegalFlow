# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, example="Apa sanksi tidak daftar PSE?")
    thread_id: str = Field(..., description="UUID unik untuk sesi percakapan")

class ChatResponse(BaseModel):
    response: str
    thread_id: str