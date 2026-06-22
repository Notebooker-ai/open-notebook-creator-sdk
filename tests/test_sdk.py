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
