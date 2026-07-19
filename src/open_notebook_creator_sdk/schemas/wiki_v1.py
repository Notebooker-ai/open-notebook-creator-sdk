"""wiki.v1 — a set of interlinked topic articles synthesized from a notebook.

Unlike essay/textbook (whose substance lives in files), the articles live in
``data`` so the creator's view bundle can render a navigable wiki (topic index,
[[wikilinks]], footnote citations). The Obsidian-ready ``.md`` files and vault
zip attached in ``CreationResult.files`` are derived from this same data.
IMMUTABLE shape — additive optional only.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "wiki.v1"


class WikiSourceRefV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Citation marker ("s1", "s2", ...) matching ``[^s1]`` footnote refs in
    # ``body_markdown``. Markers are unique per topic, not per wiki.
    marker: str
    title: str
    url: Optional[str] = None
    # Host Source record id (provenance only; may not resolve after deletion).
    source_id: Optional[str] = None


class WikiTopicV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Display title, e.g. "Rosé Wine".
    name: str
    # URL-safe id, unique within the wiki (view navigation key).
    slug: str
    # Emitted .md filename (post-sanitization), e.g. "Rosé Wine.md". Wikilinks
    # in ``body_markdown`` target other topics' filename stems.
    filename: str
    # Plain-text lede (first paragraph, markers/markdown stripped).
    summary: Optional[str] = None
    # Resolved markdown: [[Stem]] / [[Stem|anchor]] wikilinks and [^sN] footnote
    # refs. Contains NO footnote-definition block — renderers and exporters
    # derive References from ``sources`` so the two never drift.
    body_markdown: str
    sources: List[WikiSourceRefV1] = Field(default_factory=list)


class WikiV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Wiki title (drives the zip name and the index note's H1).
    title: str
    description: Optional[str] = None
    topics: List[WikiTopicV1] = Field(default_factory=list)
    # Filename of the emitted index/MOC note (e.g. "Wiki Index.md"), when one
    # was generated.
    index_filename: Optional[str] = None
