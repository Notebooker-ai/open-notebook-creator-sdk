"""socratic.v1 — a precomputed Socratic tutoring session over notebook content.

The full dialogue tree is generated up front: every nugget carries its question,
a self-assessment checklist (``expected_points``), misconception probes, an
escalating hint ladder (sub-questions, not statements), and a citation-pinned
reveal. The creator's view bundle runs the tutoring loop entirely client-side —
no runtime LLM — so the tutor structurally cannot "cave" and answer early: the
reveal is simply not shown until the flow reaches it.

Data-only (an optional printable transcript ships in ``CreationResult.files``).
IMMUTABLE shape — additive optional only.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "socratic.v1"

QuestionType = Literal[
    "clarifying", "probing", "connecting", "counter", "hypothetical"
]


class SocraticProbe(BaseModel):
    """A tappable misconception: its short label and the counter-question that
    exposes the contradiction (never a correction)."""

    model_config = ConfigDict(extra="forbid")

    label: str
    question: str


class SocraticReveal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str
    citations: List[str] = Field(
        default_factory=list, description="source ids from ContentBundle.sources"
    )


class SocraticNugget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    kind: Literal["concept", "synthesis"] = "concept"
    requires: List[str] = Field(
        default_factory=list,
        description="nugget ids that must be completed first (synthesis gating)",
    )
    source_ids: List[str] = Field(default_factory=list)
    question: str
    question_type: QuestionType = "probing"
    expected_points: List[str] = Field(
        default_factory=list, description="self-assessment checklist"
    )
    hints: List[str] = Field(
        default_factory=list,
        description="escalating sub-questions; only the last may near-reveal",
    )
    misconceptions: List[SocraticProbe] = Field(default_factory=list)
    reveal: SocraticReveal
    deeper: Optional[str] = None  # optional stretch follow-up after mastery


class SocraticV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    persona: str
    difficulty: Literal["recall", "application", "synthesis"] = "application"
    allow_reveal: bool = Field(
        default=True,
        description="False = pure Socratic: the view never shows model answers",
    )
    nuggets: List[SocraticNugget] = Field(default_factory=list)
