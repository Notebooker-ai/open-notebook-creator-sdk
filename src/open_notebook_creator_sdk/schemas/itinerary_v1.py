"""``itinerary.v1`` — a day-by-day plan composed from notebook content.

General by design: days hold ordered stops with optional free-text time
labels; anything extracted but not scheduled lands in ``unscheduled`` so no
content is silently dropped. Nothing here is travel-specific — the same shape
renders a trip, a conference plan, or a study week.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ItineraryStopV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    time_label: Optional[str] = Field(
        default=None, description="Free text: '9:00 AM', 'Morning', 'After dinner'"
    )
    description: Optional[str] = None
    location: Optional[str] = Field(
        default=None, description="Short free-text area, neighborhood, or venue"
    )
    duration: Optional[str] = Field(
        default=None, description="Free text: '2h', '45 min', 'half day'"
    )
    tip: Optional[str] = Field(
        default=None, description="One practical, source-derived note"
    )


class ItineraryDayV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(description="'Day 1', 'Saturday', …")
    date: Optional[str] = Field(default=None, description="ISO date when known")
    theme: Optional[str] = Field(
        default=None, description="Short day theme, e.g. 'Old town + museums'"
    )
    stops: List[ItineraryStopV1] = Field(default_factory=list)


class ItineraryV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = None
    destination: Optional[str] = None
    days: List[ItineraryDayV1] = Field(default_factory=list)
    unscheduled: List[ItineraryStopV1] = Field(
        default_factory=list,
        description="Extracted stops that were not placed into any day",
    )
