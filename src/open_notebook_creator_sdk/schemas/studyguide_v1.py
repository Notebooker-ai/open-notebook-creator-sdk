"""studyguide.v1 — a study guide rendered to files (HTML/PDF) via Quarto.

Like textbook.v1, the substance (concept summaries, "need to know" bullets, common
traps, glossary) lives in ``CreationResult.files``; ``data`` carries only the
metadata the host UI needs (title, topic list, formats). IMMUTABLE shape — additive
optional only.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "studyguide.v1"


class StudyGuideTopic(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    summary: Optional[str] = None


class StudyGuideV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    topics: List[StudyGuideTopic] = Field(default_factory=list)
    # Formats successfully rendered, e.g. ["html", "pdf"].
    formats: List[str] = Field(default_factory=list)
