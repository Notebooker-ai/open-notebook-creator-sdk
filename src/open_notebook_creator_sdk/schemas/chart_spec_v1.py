"""chart_spec.v1 — one or more AntV G2 (v5) chart specs rendered client-side.

The ``specs`` entries are passed (nearly) verbatim to G2's ``chart.options(spec)``;
we keep each spec loosely typed on purpose so new G2 features need no schema bump.
IMMUTABLE shape — additive optional fields only.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "chart_spec.v1"


class ChartSpecV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    library: str = "antv-g2"
    title: Optional[str] = None
    specs: List[Dict[str, Any]] = Field(
        default_factory=list, description="G2 v5 spec objects"
    )
