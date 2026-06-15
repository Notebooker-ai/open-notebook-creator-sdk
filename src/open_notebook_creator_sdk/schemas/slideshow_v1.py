"""slideshow.v1 — a slide deck rendered to files (reveal.js HTML / PPTX / PDF) via Quarto.

The LLM designs a sequence of typed slides; data slides (chart/infographic) embed AntV
visuals pre-rendered to static images. Like textbook.v1, the substance lives in
``CreationResult.files``; ``data`` carries only the metadata the host UI needs (title,
slide summary, which formats were produced). IMMUTABLE shape — additive optional only.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "slideshow.v1"


class SlideSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # "title" | "section" | "bullets" | "image_text" | "chart" | "infographic"
    type: str
    title: Optional[str] = None


class SlideshowV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    subtitle: Optional[str] = None
    theme: str = "auto"
    slides: List[SlideSummary] = Field(default_factory=list)
    # Formats successfully rendered, e.g. ["html", "pptx", "pdf"].
    formats: List[str] = Field(default_factory=list)
