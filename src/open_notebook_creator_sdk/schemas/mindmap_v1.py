"""mindmap.v1 — a single mermaid mindmap rendered client-side.

``mermaid_syntax`` holds the raw mermaid ``mindmap`` source verbatim; the frontend
feeds it straight to ``mermaid.render`` and exports it as markdown / PNG / SVG. We
keep the payload to the source string (plus title/description) on purpose so new
mermaid features need no schema bump. IMMUTABLE shape — additive optional fields only.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "mindmap.v1"


class MindmapV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    mermaid_syntax: str = Field(description="Mermaid mindmap source")
    description: Optional[str] = None
