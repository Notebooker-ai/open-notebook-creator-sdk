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
from .flashcards_v1 import FlashcardsV1

SCHEMA_REGISTRY: Dict[str, Type[BaseModel]] = {
    "flashcards.v1": FlashcardsV1,
    "chart_spec.v1": ChartSpecV1,
    "audio.v1": AudioV1,
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
    "AudioV1",
]
