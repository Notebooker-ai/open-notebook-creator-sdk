"""essay.v1 — a thesis-driven essay rendered to files (HTML/PDF) via Quarto.

Like textbook.v1, the essay's substance lives in ``CreationResult.files``; ``data``
carries only the metadata the host UI needs (title, thesis, variant, formats).
IMMUTABLE shape — additive optional only.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "essay.v1"


class EssayV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    thesis: Optional[str] = None
    # "argumentative" | "expository" | "comparative"
    variant: str = "argumentative"
    # Formats successfully rendered, e.g. ["html", "pdf"].
    formats: List[str] = Field(default_factory=list)
