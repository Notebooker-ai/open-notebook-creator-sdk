"""website.v1 — a multi-page static website rendered to files (Quarto).

Files-first like textbook.v1: the substance is the rendered site zip in
``CreationResult.files``; ``data`` carries the metadata the host UI needs
(title, page list, theme) plus publish state that the HOST writes after
uploading the extracted site to public storage (``published_url`` /
``published_files``). IMMUTABLE shape — additive optional only.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "website.v1"


class WebsitePage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    slug: str
    summary: Optional[str] = None
    source_ids: List[str] = Field(default_factory=list)


class WebsiteV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = None
    theme: str = "cosmo"
    pages: List[WebsitePage] = Field(default_factory=list)
    # Publish state — written by the host's publish endpoint, not the creator.
    published_url: Optional[str] = None
    published_files: List[str] = Field(default_factory=list)
