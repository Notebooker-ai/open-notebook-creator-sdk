"""flashcards.v1 — a deck of Q/A cards for in-app study and Anki export.

IMMUTABLE: never edit this shape in place. Additive optional fields only; any
breaking change ships as flashcards.v2 with its own renderer.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "flashcards.v1"


class Flashcard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    front: str
    back: str
    tags: List[str] = Field(default_factory=list)


class FlashcardsV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    deck_name: str
    cards: List[Flashcard]
