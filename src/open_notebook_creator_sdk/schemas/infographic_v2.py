"""infographic.v2 — a rich, illustrated infographic rendered client-side by the
AntV Infographic engine (https://infographic.antv.vision/).

Unlike infographic.v1 (a fixed set of stat/text/list/quote cards), v2 carries a
single ``spec`` string written in AntV's declarative infographic DSL, e.g.::

    infographic list-row-horizontal-icon-arrow
    data
      title Product growth
      lists
        - label Acquire
          icon rocket

The frontend passes ``spec`` to ``new Infographic(...).render(spec)``, which
yields an SVG. Both the ``infographics`` (non-chart templates) and ``charts``
(chart-* templates) creators emit this one schema. The DSL is the contract; we
keep ``spec`` an opaque string so new AntV templates need no schema bump.
IMMUTABLE shape — additive optional fields only.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "infographic.v2"


class InfographicV2(BaseModel):
    model_config = ConfigDict(extra="forbid")

    library: str = "antv-infographic"
    title: Optional[str] = None
    spec: str = Field(default="", description="AntV Infographic DSL string")
    # AntV theme name; "auto" follows the app's light/dark mode (resolved client-side).
    theme: Optional[str] = None
