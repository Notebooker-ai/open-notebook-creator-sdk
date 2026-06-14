"""infographic.v1 — a composed, designed infographic (no charts).

A themed poster of blocks rendered client-side: headline + key-stat cards,
insight text, bulleted takeaways, and quotes. (Data charts live in chart_spec.v1.)

A single "wide" block model is used (rather than a discriminated union) so the
JSON-Schema -> TS/Zod codegen stays simple. ``type`` selects which fields apply;
the renderer reads the relevant ones. IMMUTABLE shape — additive optional only.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "infographic.v1"


class InfographicBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["stat", "text", "list", "quote"]
    # stat
    value: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None  # lucide icon name hint
    # text
    heading: Optional[str] = None
    body: Optional[str] = None
    # list
    items: Optional[List[str]] = None
    # quote
    text: Optional[str] = None
    attribution: Optional[str] = None


class InfographicV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    subtitle: Optional[str] = None
    blocks: List[InfographicBlock] = Field(default_factory=list)
