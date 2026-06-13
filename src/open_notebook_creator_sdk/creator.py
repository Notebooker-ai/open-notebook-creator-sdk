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
