"""The creator contract: a manifest (static metadata) + an async ``generate``.

A creator MUST be **stateless per call** — no module-global mutable config, no
process-wide "current user", no cached credential-bearing clients. The host runs
creators concurrently in one worker process; shared state cross-contaminates jobs.
The compliance suite (:mod:`open_notebook_creator_sdk.testing`) enforces this.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Optional, Type

from pydantic import BaseModel, Field

from .models import CreationRequest, CreationResult


class ModelRoleSpec(BaseModel):
    """A model the creator needs. Capability-oriented so the host's model picker
    only offers models that will actually work at runtime."""

    key: str
    kind: str  # "language" | "text_to_speech" | "embedding" | ...
    requires: List[str] = Field(
        default_factory=list, description="e.g. 'structured_json', 'tool_calling'"
    )
    min_context_window: Optional[int] = None
    provider_allowlist: Optional[List[str]] = None
    params_schema: Optional[Dict[str, Any]] = None
    required: bool = True
    description: str = ""


class CreatorView(BaseModel):
    """Points at a creator's self-contained HTML *view bundle*, shipped inside the
    plugin package, that owns rendering its artifacts.

    The host serves ``entry`` (``GET /creation/creators/{key}/view``) and renders it
    in a **sandboxed** iframe (opaque origin — it cannot read host state), then posts
    the artifact in via ``postMessage``:

        {type: "open-notebook:artifact", schema_id, name, data, config, theme}

    The bundle should ``postMessage({type: "open-notebook:ready"})`` to its parent
    once listening (the host also posts on iframe ``load``, covering either order),
    then **dispatch on ``schema_id``**. Crucially, a bundle MUST keep a renderer for
    every ``schema_id`` the creator has *ever* emitted, so a newer plugin still
    displays artifacts created under an older schema version. The bundle is
    display-only: it never writes back to the host API.
    """

    entry: str = Field(
        ...,
        description="package-relative path to the view HTML, e.g. 'view/index.html'",
    )


class CreatorManifest(BaseModel):
    """Static description of a creator. Surfaced to the frontend via
    ``GET /creation/creators`` to drive nav, config forms, and model pickers."""

    key: str
    name: str
    version: str
    description: str = ""
    sdk_compat: str = Field(..., description="PEP 440 specifier, e.g. '>=0.1,<1'")
    emits: List[str] = Field(..., description="schema ids this creator can produce")
    model_roles: List[ModelRoleSpec] = Field(default_factory=list)
    config_schema: Dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema built from config_model"
    )
    icon: Optional[str] = None
    has_custom_form: bool = False
    view: Optional[CreatorView] = Field(
        default=None,
        description="self-contained HTML view bundle the plugin ships and the host iframes",
    )


class BaseCreator(ABC):
    """Subclass this in a plugin package and expose it via the
    ``open_notebook.creators`` entry point.
    """

    #: Pydantic model describing per-generation config; its JSON Schema drives the form.
    config_model: ClassVar[Type[BaseModel]]

    @property
    @abstractmethod
    def manifest(self) -> CreatorManifest: ...

    @abstractmethod
    async def generate(self, request: CreationRequest) -> CreationResult: ...

    # --- convenience -------------------------------------------------------

    def build_manifest(self, **kwargs: Any) -> CreatorManifest:
        """Helper to assemble a manifest, auto-deriving ``config_schema`` from
        ``config_model`` so subclasses don't hand-write JSON Schema."""
        kwargs.setdefault("config_schema", self.config_model.model_json_schema())
        return CreatorManifest(**kwargs)
