"""timeline.v1 — a chronological timeline rendered client-side (vis-timeline).

Data-only (no files): the LLM produces a set of dated items (and optional lane
groups) shaped to the vis-timeline DataSet. The frontend builds the interactive
timeline directly from ``items``/``groups``. IMMUTABLE shape — additive optional only.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "timeline.v1"


class TimelineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    content: str  # label shown on the item
    start: str  # ISO date/datetime or year
    end: Optional[str] = None  # set for ranges
    group: Optional[str] = None  # lane id (matches a TimelineGroup.id)
    type: Optional[str] = None  # vis-timeline item type: point|range|box|background


class TimelineGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    content: str  # lane label


class TimelineV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    items: List[TimelineItem] = Field(default_factory=list)
    groups: List[TimelineGroup] = Field(default_factory=list)
