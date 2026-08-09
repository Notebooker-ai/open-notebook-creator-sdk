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

    def create_image(self, **extra_config: Any) -> "ImageGenerationModel":
        """Build an image-generation client speaking the OpenAI Images API
        (``POST {base_url}/images/generations``, ``response_format=b64_json``).

        Esperanto has no image modality, so this uses its own thin transport
        (requires the optional ``httpx`` dependency). Works against OpenAI and
        any OpenAI-compatible gateway. ``config`` must provide ``api_key`` and
        may provide ``base_url`` (default ``https://api.openai.com/v1``)."""
        config = {**self.config, **extra_config}
        return ImageGenerationModel(
            provider=self.provider, model=self.model, config=config
        )


class ImageGenerationModel:
    """Minimal async client for the OpenAI-shaped Images API."""

    def __init__(self, provider: str, model: str, config: Dict[str, Any]):
        self.provider = provider
        self.model = model
        self._api_key = config.get("api_key")
        self._base_url = (config.get("base_url") or "https://api.openai.com/v1").rstrip("/")
        self._timeout = float(config.get("timeout", 120))
        # Per-user attribution headers the host injects into every model
        # config (e.g. X-User-Id, which the Notebooker gateway REQUIRES —
        # without it every image call 400s "Missing X-User-Id header").
        # Esperanto's language clients forward these; this transport must too.
        self._extra_headers: Dict[str, str] = {
            **(config.get("default_headers") or {}),
            **(config.get("extra_headers") or {}),
        }

    _MAX_ATTEMPTS = 3
    _BACKOFF_BASE_S = 1.0

    async def agenerate_image(self, prompt: str, size: str = "1024x1024") -> bytes:
        """Generate one image; returns raw image bytes.

        Retries 5xx responses and transport errors with exponential backoff —
        diffusion backends flake transiently and a background image is not
        worth failing a whole creation over. 4xx raises immediately (a bad
        request won't get better by retrying)."""
        import asyncio
        import base64

        import httpx  # optional dependency of image-consuming creators

        headers = {"Content-Type": "application/json", **self._extra_headers}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "b64_json",
        }
        body = None
        last_error: Exception | None = None
        for attempt in range(self._MAX_ATTEMPTS):
            if attempt:
                await asyncio.sleep(self._BACKOFF_BASE_S * 2 ** (attempt - 1))
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    resp = await client.post(
                        f"{self._base_url}/images/generations",
                        json=payload,
                        headers=headers,
                    )
                if resp.status_code >= 500:
                    resp.raise_for_status()  # raises HTTPStatusError -> retried
                resp.raise_for_status()  # 4xx raises here and is NOT retried
                body = resp.json()
                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code < 500:
                    raise
                last_error = e
            except httpx.TransportError as e:
                last_error = e
        if body is None:
            assert last_error is not None
            raise last_error
        data = (body.get("data") or [{}])[0]
        b64 = data.get("b64_json")
        if b64:
            return base64.b64decode(b64)
        url = data.get("url")
        if url:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                img = await client.get(url)
                img.raise_for_status()
                return img.content
        raise ValueError("image response contained neither b64_json nor url")


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
