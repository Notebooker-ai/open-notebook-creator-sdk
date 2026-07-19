"""flint.v1 — a chart described as a Microsoft Flint (flint-chart) unified input,
rendered client-side by the charts creator's view bundle.

Flint (https://github.com/microsoft/flint-chart) compiles one library-agnostic
``input`` — ``{data, semantic_types, chart_spec}`` — into a native spec for one of
three rendering libraries: Vega-Lite, ECharts, or Chart.js. The frontend calls the
matching ``assemble*`` function for ``library`` and renders the result. Browse
examples at https://microsoft.github.io/flint-chart/#/gallery.

We keep ``input`` loosely typed on purpose (like chart_spec.v1's ``specs``) so new
Flint chart types / encodings need no schema bump. IMMUTABLE shape — additive
optional fields only.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "flint.v1"


class FlintV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Rendering backend: "vega-lite", "echarts", or "chartjs". Kept a plain string
    # so new Flint backends need no schema bump.
    library: str = "vega-lite"
    title: Optional[str] = None
    # Flint unified input: { data: {values|url}, semantic_types, chart_spec, options? }.
    input: Dict[str, Any] = Field(default_factory=dict, description="Flint chart assembly input")
    # "auto" follows the app's light/dark mode (resolved client-side).
    theme: Optional[str] = None
