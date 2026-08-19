"""Schemas for the NUVYRA conversational research companion."""
from typing import Literal
from pydantic import BaseModel, Field


class CompanionRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    language: Literal["en", "hi", "fr"] = "en"


class CompanionResponse(BaseModel):
    answer: str
    category: Literal["system", "research", "health", "safety"]
    disclaimer: str
