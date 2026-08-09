"""story.v1 — an illustrated, optionally branching story built from sources.

One schema for every narrative form (``story_type``): picture books, short
stories, fables, bedtime stories, and branching adventures. Pages form a
graph: each page has a stable ``id`` and optional ``choices`` pointing at
other page ids; a linear story is simply a graph with no choices, read in
``number`` order, while an adventure starts at ``start_page_id`` and follows
the reader's picks.

Illustrations are diffusion-generated raster art: each page may carry a
full-page illustration (``image_data_uri``); character identity across pages
is anchored by a locked per-character ``visual`` spec (and, where the image
backend supports reference conditioning, a shared cast-sheet image). Legacy
artifacts from the structural-SVG era may instead carry a sanitized per-page
``svg`` and per-setting ``background_data_uri`` — renderers must keep
displaying those. IMMUTABLE shape — additive optional only.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "story.v1"


class StoryCharacter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str = ""
    # Canonical locked appearance spec (species/age, build, hair/features,
    # clothing with named colors, signature accessory) embedded verbatim in
    # every illustration prompt so identity survives across pages.
    visual: str = ""


class StorySetting(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str = ""
    # Legacy (structural-SVG era): per-setting diffusion background layered
    # behind the page's vector scene. No longer written; renderers keep it
    # for old artifacts.
    background_data_uri: Optional[str] = None


class StoryChoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    target_page_id: str


class StoryPage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    number: int
    text: str
    setting_id: Optional[str] = None
    character_ids: List[str] = Field(default_factory=list)
    # Full-page diffusion illustration, stored as a compressed data URI so
    # view bundles and published shells stay self-contained.
    image_data_uri: Optional[str] = None
    svg: Optional[str] = None  # legacy sanitized SVG; no longer written
    choices: List[StoryChoice] = Field(default_factory=list)
    is_ending: bool = False


class StoryV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    dedication: Optional[str] = None
    story_type: str = "short-story"  # picture-book | short-story | fable | bedtime | adventure
    reading_age: str = "all-ages"
    style: str = "paper-cutout"
    moral: Optional[str] = None  # fables
    palette: List[str] = Field(default_factory=list)  # hex colors
    characters: List[StoryCharacter] = Field(default_factory=list)
    settings: List[StorySetting] = Field(default_factory=list)
    pages: List[StoryPage] = Field(default_factory=list)
    start_page_id: Optional[str] = None  # adventures; defaults to first page
    # Publish state — written by the host's publish endpoint, not the creator.
    published_url: Optional[str] = None
    published_files: List[str] = Field(default_factory=list)
