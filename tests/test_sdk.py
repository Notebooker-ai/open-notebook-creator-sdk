"""SDK self-tests: DTO round-trips, schema validation, credential non-leakage,
codegen smoke test, and a dummy compliant creator."""

from __future__ import annotations

import asyncio

import pytest

from open_notebook_creator_sdk import (
    BaseCreator,
    ContentBundle,
    CreationRequest,
    CreationResult,
    ModelRole,
    validate_artifact_data,
)
from open_notebook_creator_sdk.codegen import generate
from open_notebook_creator_sdk.testing import (
    assert_creator_compliant,
    assert_result_compliant,
)
from pydantic import BaseModel


def test_credentials_excluded_from_serialization():
    role = ModelRole(provider="openai", model="gpt-4o", config={"api_key": "secret-xyz"})
    dumped = role.model_dump_json()
    assert "secret-xyz" not in dumped
    assert "api_key" not in dumped
    assert "secret-xyz" not in repr(role)
    # but still usable in-process
    assert role.config["api_key"] == "secret-xyz"


def test_credentials_not_in_request_dump():
    req = CreationRequest(
        content=ContentBundle(text="hi"),
        models={"text": ModelRole(provider="openai", model="x", config={"api_key": "K"})},
        output_dir="/tmp/x",
        artifact_id="a1",
    )
    assert "K" not in req.model_dump_json()


def test_schema_validation_roundtrip():
    data = {"deck_name": "Deck", "cards": [{"id": "1", "front": "Q", "back": "A"}]}
    obj = validate_artifact_data("flashcards.v1", data)
    assert obj.cards[0].front == "Q"


def test_schema_rejects_extra_fields():
    with pytest.raises(Exception):
        validate_artifact_data(
            "flashcards.v1", {"deck_name": "D", "cards": [], "bogus": 1}
        )


def test_unknown_schema_raises():
    with pytest.raises(KeyError):
        validate_artifact_data("does.not.exist", {})


def test_mindmap_schema_roundtrip():
    data = {
        "title": "Photosynthesis",
        "mermaid_syntax": "mindmap\n  root((Photosynthesis))\n    Light\n    Dark",
        "description": "How plants convert light to energy",
    }
    obj = validate_artifact_data("mindmap.v1", data)
    assert obj.title == "Photosynthesis"
    assert obj.mermaid_syntax.startswith("mindmap")


def test_mindmap_schema_rejects_extra_fields():
    with pytest.raises(Exception):
        validate_artifact_data(
            "mindmap.v1", {"title": "T", "mermaid_syntax": "mindmap", "bogus": 1}
        )


def test_wiki_schema_roundtrip():
    data = {
        "title": "My Wine Wiki",
        "description": "Topics distilled from my saved sources",
        "topics": [
            {
                "name": "Rosé Wine",
                "slug": "rose-wine",
                "filename": "Rosé Wine.md",
                "summary": "Pink wine made from red grapes.",
                "body_markdown": "Rosé is made by limiting skin contact.[^s1] See [[Provence]].",
                "sources": [
                    {
                        "marker": "s1",
                        "title": "Rosé thread",
                        "url": "https://example.com/rose",
                        "source_id": "source:abc",
                    }
                ],
            }
        ],
        "index_filename": "Wiki Index.md",
    }
    obj = validate_artifact_data("wiki.v1", data)
    assert obj.topics[0].sources[0].marker == "s1"
    assert obj.index_filename == "Wiki Index.md"


def test_wiki_schema_rejects_extra_fields():
    with pytest.raises(Exception):
        validate_artifact_data("wiki.v1", {"title": "T", "topics": [], "bogus": 1})


def test_codegen_emits_validators():
    code = generate()
    assert "FlashcardsV1Schema" in code
    assert "SCHEMA_VALIDATORS" in code
    assert '"flashcards.v1"' in code


class _DummyConfig(BaseModel):
    n: int = 3


class _DummyCreator(BaseCreator):
    config_model = _DummyConfig

    @property
    def manifest(self):
        return self.build_manifest(
            key="dummy",
            name="Dummy",
            version="0.1.0",
            sdk_compat=">=0.1,<1",
            emits=["flashcards.v1"],
        )

    async def generate(self, request: CreationRequest) -> CreationResult:
        return CreationResult(
            status="SUCCESS",
            schema_id="flashcards.v1",
            data={"deck_name": "D", "cards": [{"id": "1", "front": "Q", "back": "A"}]},
        )


def test_manifest_view_roundtrips():
    from open_notebook_creator_sdk import CreatorManifest, CreatorView

    m = CreatorManifest(
        key="k",
        name="N",
        version="1.0.0",
        sdk_compat=">=0.4,<1",
        emits=["flashcards.v1"],
        view=CreatorView(entry="view/index.html"),
    )
    assert m.view is not None and m.view.entry == "view/index.html"
    # absent by default — creators without a bundle stay valid
    m2 = CreatorManifest(
        key="k", name="N", version="1.0.0", sdk_compat=">=0.1,<1", emits=["x"]
    )
    assert m2.view is None
    # accepts a plain dict too (host reads it defensively)
    assert "view/index.html" in m.model_dump_json()


def test_dummy_creator_compliant():
    creator = _DummyCreator()
    assert_creator_compliant(creator)
    result = asyncio.new_event_loop().run_until_complete(
        creator.generate(
            CreationRequest(
                content=ContentBundle(text="x"), output_dir="/tmp", artifact_id="a"
            )
        )
    )
    assert_result_compliant(creator, result)


@pytest.mark.asyncio
async def test_image_client_forwards_attribution_headers(monkeypatch):
    """The host injects per-user headers (X-User-Id) into model config; the
    image transport must send them — the Notebooker gateway 400s without."""
    from open_notebook_creator_sdk.models import ImageGenerationModel

    captured = {}

    class _FakeResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            import base64

            return {"data": [{"b64_json": base64.b64encode(b"png").decode()}]}

    class _FakeClient:
        def __init__(self, timeout=None):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, json=None, headers=None):
            captured["url"] = url
            captured["headers"] = headers
            return _FakeResponse()

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)

    model = ImageGenerationModel(
        provider="openai_compatible",
        model="Notebooker Image",
        config={
            "api_key": "k",
            "base_url": "https://ai.example/v1",
            "extra_headers": {"X-User-Id": "user:42"},
        },
    )
    out = await model.agenerate_image("a fox", size="1024x1024")
    assert out == b"png"
    assert captured["headers"]["X-User-Id"] == "user:42"
    assert captured["headers"]["Authorization"] == "Bearer k"


@pytest.mark.asyncio
async def test_image_client_retries_5xx_then_succeeds(monkeypatch):
    """Diffusion backends flake; a 500 must be retried with backoff instead of
    failing the whole creation. 4xx must fail fast."""
    import base64

    import httpx

    from open_notebook_creator_sdk.models import ImageGenerationModel

    posts = []

    def make_client(statuses):
        class _Resp:
            def __init__(self, status):
                self.status_code = status

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise httpx.HTTPStatusError(
                        f"{self.status_code}", request=None, response=self
                    )

            def json(self):
                return {"data": [{"b64_json": base64.b64encode(b"img").decode()}]}

        class _Client:
            def __init__(self, timeout=None):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, url, json=None, headers=None):
                posts.append(url)
                return _Resp(statuses[min(len(posts) - 1, len(statuses) - 1)])

        return _Client

    async def no_sleep(_):
        pass

    monkeypatch.setattr("asyncio.sleep", no_sleep)

    # 500, 500, then 200 -> succeeds on the third attempt.
    monkeypatch.setattr(httpx, "AsyncClient", make_client([500, 500, 200]))
    model = ImageGenerationModel(
        provider="openai_compatible", model="m", config={"api_key": "k"}
    )
    assert await model.agenerate_image("a fox") == b"img"
    assert len(posts) == 3

    # Persistent 500 -> raises after max attempts.
    posts.clear()
    monkeypatch.setattr(httpx, "AsyncClient", make_client([500]))
    with pytest.raises(httpx.HTTPStatusError):
        await model.agenerate_image("a fox")
    assert len(posts) == 3

    # 400 -> immediate failure, exactly one request.
    posts.clear()
    monkeypatch.setattr(httpx, "AsyncClient", make_client([400]))
    with pytest.raises(httpx.HTTPStatusError):
        await model.agenerate_image("a fox")
    assert len(posts) == 1


@pytest.mark.asyncio
async def test_image_edit_sends_multipart_references(monkeypatch):
    """agenerate_image_edit must hit /images/edits with the reference bytes as
    multipart file parts and the usual auth/attribution headers."""
    import base64

    import httpx

    from open_notebook_creator_sdk.models import ImageGenerationModel

    captured = {}

    class _FakeResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"data": [{"b64_json": base64.b64encode(b"edited").decode()}]}

    class _FakeClient:
        def __init__(self, timeout=None):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, data=None, files=None, headers=None):
            captured.update(url=url, data=data, files=files, headers=headers)
            return _FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)

    model = ImageGenerationModel(
        provider="openai_compatible",
        model="img-model",
        config={
            "api_key": "k",
            "base_url": "https://ai.example/v1",
            "extra_headers": {"X-User-Id": "user:42"},
        },
    )
    out = await model.agenerate_image_edit("same cast, new scene", [b"ref1", b"ref2"])
    assert out == b"edited"
    assert captured["url"] == "https://ai.example/v1/images/edits"
    assert captured["data"]["model"] == "img-model"
    assert captured["data"]["prompt"] == "same cast, new scene"
    assert [f[1][1] for f in captured["files"]] == [b"ref1", b"ref2"]
    assert all(f[0] == "image[]" for f in captured["files"])
    # Multipart: httpx must set the boundary Content-Type itself.
    assert "Content-Type" not in captured["headers"]
    assert captured["headers"]["Authorization"] == "Bearer k"
    assert captured["headers"]["X-User-Id"] == "user:42"


@pytest.mark.asyncio
async def test_image_edit_fails_fast_on_4xx_and_requires_references(monkeypatch):
    """A 4xx from /images/edits means 'unsupported here' — exactly one request,
    no retries, so callers can fall back to plain generations cheaply."""
    import httpx

    from open_notebook_creator_sdk.models import ImageGenerationModel

    posts = []

    class _Resp:
        status_code = 404

        def raise_for_status(self):
            raise httpx.HTTPStatusError("404", request=None, response=self)

        def json(self):
            return {}

    class _Client:
        def __init__(self, timeout=None):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, data=None, files=None, headers=None):
            posts.append(url)
            return _Resp()

    monkeypatch.setattr(httpx, "AsyncClient", _Client)
    model = ImageGenerationModel(
        provider="openai_compatible", model="m", config={"api_key": "k"}
    )
    with pytest.raises(httpx.HTTPStatusError):
        await model.agenerate_image_edit("scene", [b"ref"])
    assert len(posts) == 1

    with pytest.raises(ValueError):
        await model.agenerate_image_edit("scene", [])
    assert len(posts) == 1  # no request without references
