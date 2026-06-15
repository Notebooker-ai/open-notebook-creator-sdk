"""Registry of versioned artifact data schemas.

``schema_id`` strings (e.g. ``flashcards.v1``) are the durable cross-language
contract: the host validates ``CreationResult.data`` against these Pydantic
models, and the frontend keys its renderers off the same strings (via generated
TypeScript/Zod). Schemas are immutable — new behavior means a new id.
"""

from __future__ import annotations

from typing import Dict, Type

from pydantic import BaseModel

from .audio_v1 import AudioV1
from .chart_spec_v1 import ChartSpecV1
from .essay_v1 import EssayV1
from .flashcards_v1 import FlashcardsV1
from .infographic_v1 import InfographicV1
from .infographic_v2 import InfographicV2
from .mindmap_v1 import MindmapV1
from .slideshow_v1 import SlideshowV1
from .studyguide_v1 import StudyGuideV1
from .textbook_v1 import TextbookV1
from .timeline_v1 import TimelineV1

SCHEMA_REGISTRY: Dict[str, Type[BaseModel]] = {
    "flashcards.v1": FlashcardsV1,
    "chart_spec.v1": ChartSpecV1,
    "infographic.v1": InfographicV1,
    "infographic.v2": InfographicV2,
    "mindmap.v1": MindmapV1,
    "audio.v1": AudioV1,
    "textbook.v1": TextbookV1,
    "essay.v1": EssayV1,
    "studyguide.v1": StudyGuideV1,
    "slideshow.v1": SlideshowV1,
    "timeline.v1": TimelineV1,
}


def get_schema(schema_id: str) -> Type[BaseModel]:
    if schema_id not in SCHEMA_REGISTRY:
        raise KeyError(f"Unknown schema id: {schema_id}")
    return SCHEMA_REGISTRY[schema_id]


def validate_artifact_data(schema_id: str, data: dict) -> BaseModel:
    """Validate (and coerce) ``data`` against the named schema; raises on mismatch."""
    return get_schema(schema_id).model_validate(data)


__all__ = [
    "SCHEMA_REGISTRY",
    "get_schema",
    "validate_artifact_data",
    "FlashcardsV1",
    "ChartSpecV1",
    "InfographicV1",
    "InfographicV2",
    "MindmapV1",
    "AudioV1",
    "TextbookV1",
    "EssayV1",
    "StudyGuideV1",
    "SlideshowV1",
    "TimelineV1",
]
