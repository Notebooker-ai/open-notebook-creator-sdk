"""audio.v1 — a generated audio artifact (e.g. a podcast). The audio binary
lives in ``CreationResult.files``; this payload carries the structured outputs.

Used to retrofit podcast-creator onto the contract. IMMUTABLE shape.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "audio.v1"


class AudioV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transcript: Optional[List[Dict[str, Any]]] = None
    outline: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[float] = None
