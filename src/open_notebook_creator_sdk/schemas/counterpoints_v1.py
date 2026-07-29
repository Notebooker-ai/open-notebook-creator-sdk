"""counterpoints.v1 — two-sided debates on issues drawn from a notebook.

Each issue frames a debatable question with two named sides and a list of
matched argument pairs: a ``point`` for side A, the strongest ``counterpoint``
from side B, and (optionally) side A's ``response`` to that counter. The
substance lives in ``data`` so the creator's view bundle can render an
interactive two-column debate; PDF/Markdown files in ``CreationResult.files``
are derived from this same data. IMMUTABLE shape — additive optional only.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "counterpoints.v1"


class CounterpointPairV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Side A's claim, stated affirmatively.
    point: str
    # Supporting evidence/reasoning for the point (from the notebook content).
    point_evidence: Optional[str] = None
    # Side B's strongest direct rebuttal to this specific point.
    counterpoint: str
    # Supporting evidence/reasoning for the counterpoint.
    counterpoint_evidence: Optional[str] = None
    # Side A's response to the counterpoint (steel-manned, not dismissive).
    response: Optional[str] = None


class CounterpointIssueV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # The debatable question, phrased neutrally (e.g. "Should X do Y?").
    question: str
    # Short neutral framing of why this issue matters in the source content.
    context: Optional[str] = None
    # Display label for side A (e.g. "For", "Proponents", "Growth first").
    side_a: str
    # Display label for side B (e.g. "Against", "Skeptics", "Stability first").
    side_b: str
    pairs: List[CounterpointPairV1] = Field(default_factory=list)
    # Neutral synthesis: where the sides actually disagree and what would
    # resolve it. Never picks a winner.
    synthesis: Optional[str] = None


class CounterpointsV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = None
    issues: List[CounterpointIssueV1] = Field(default_factory=list)
