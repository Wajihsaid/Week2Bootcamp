"""
Pydantic schemas for API request/response models.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class CharacterId(str, Enum):
    HANNIBAL = "hannibal"
    HAMILCAR = "hamilcar"
    ELYSSA = "elyssa"
    UQBA = "uqba"
    KAHINA = "kahina"
    IBN_KHALDOUN = "ibn-khaldoun"
    ABU_ZAKARIYA = "abu-zakariya"
    KHEIREDDINE = "kheireddine"
    FARHAT_HACHED = "farhat-hached"


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    characterId: str
    stream: bool = True


class ChatResponse(BaseModel):
    answer: str
    character: str
    sources: List[Dict[str, Any]] = []
    entities_detected: List[Dict[str, str]] = []


class SourceDocument(BaseModel):
    event: str
    character: str
    year: str
    score: float
    preview: str


class TTSRequest(BaseModel):
    text: str
    characterId: str


class STTResponse(BaseModel):
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: Dict[str, bool]
    documents_indexed: int

