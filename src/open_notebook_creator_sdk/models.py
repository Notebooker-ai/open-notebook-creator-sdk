"""Data-transfer objects exchanged between the Open Notebook host and creators.

These are the *normalized contract*: the host builds a ``CreationRequest`` and a
creator returns a ``CreationResult``. Nothing here knows about SurrealDB, the job
queue, or HTTP — keeping creators trivially unit-testable.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ModelRole(BaseModel):
    """A resolved model the host hands to a creator for one declared role.

    ``config`` carries credential material (api keys, base urls). It is excluded
    from serialization and hidden from ``repr`` so it never leaks into logs,
    traces, persisted records, or a ``CreationResult``. The host MUST NOT persist
    ``CreationRequest.models``.
    """

    provider: str
    model: str
    config: Dict[str, Any] = Field(default_factory=dict, exclude=True, repr=False)

    def create_language(self, **extra_config: Any):
        """Build a LangChain-compatible chat model via Esperanto.

        Requires the optional ``esperanto`` extra. ``extra_config`` is merged over
        the resolved credential config, e.g.
        ``role.create_language(structured={"type": "json"}, max_tokens=4000)``."""
        from esperanto import AIFactory  # optional extra

        config = {**self.config, **extra_config}
        return AIFactory.create_language(
            self.provider, self.model, config=config
        ).to_langchain()

    def create_text_to_speech(self, **extra_config: Any):
        from esperanto import AIFactory  # optional extra

        config = {**self.config, **extra_config}
        return AIFactory.create_text_to_speech(
            self.provider, self.model, config=config
        )


class ContentBundle(BaseModel):
    """Notebook content assembled (and possibly condensed) by the host.

    Richer than a bare string so creators get provenance and can reason about
    size without re-tokenizing.
    """

    text: str
    token_count: int = 0
    condensed: bool = False
    sources: List[Dict[str, Any]] = Field(
        default_factory=list, description="provenance, e.g. [{'id':..., 'title':...}]"
    )


class CreationFile(BaseModel):
    """A file a creator produced. ``path`` MUST be relative and contained within
    ``CreationRequest.output_dir`` — the host validates this before upload."""

    filename: str
    content_type: str
    path: str
    label: Optional[str] = None


class CreationRequest(BaseModel):
    """Everything a creator needs for one generation. Stateless in / stateless out."""

    content: ContentBundle
    instructions: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    models: Dict[str, ModelRole] = Field(default_factory=dict)
    output_dir: str
    artifact_id: str
    language: Optional[str] = None
    user_id: Optional[str] = None


class CreationError(BaseModel):
    phase: str
    message: str
    retryable: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)


CreationStatus = Literal["SUCCESS", "PARTIAL", "FAILURE"]


class CreationResult(BaseModel):
    """A creator's output. ``data`` must validate against the registered schema
    named by ``schema_id`` (which must be one of the manifest's ``emits``)."""

    model_config = ConfigDict(extra="forbid")

    status: CreationStatus
    schema_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    files: List[CreationFile] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[CreationError] = Field(default_factory=list)
    user_message: Optional[str] = None
