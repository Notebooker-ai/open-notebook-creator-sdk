"""textbook.v1 — a multi-chapter textbook rendered to files (HTML/PDF/EPUB).

Unlike the JSON-drawn schemas (infographic, chart), the textbook's substance lives
in ``CreationResult.files``; ``data`` carries only the metadata the host UI needs to
present the artifact (title, chapter list, which formats were produced). IMMUTABLE
shape — additive optional only.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "textbook.v1"


class TextbookChapter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    summary: Optional[str] = None


class TextbookV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    subtitle: Optional[str] = None
    chapters: List[TextbookChapter] = Field(default_factory=list)
    # Formats successfully rendered, e.g. ["html", "pdf", "epub"].
    formats: List[str] = Field(default_factory=list)
