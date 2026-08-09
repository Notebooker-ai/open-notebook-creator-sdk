"""Manifest-level tests for ``suggestion_hint``.

The host's "Suggest" button on the *additional instructions* field prefers a
manifest-declared hint over its transitional fallback map, so the field must
survive validation and serialization — and manifests predating it must keep
validating unchanged.
"""

from __future__ import annotations

from open_notebook_creator_sdk import BaseCreator, CreatorManifest
from pydantic import BaseModel

HINT = (
    "which chronological thread to trace, the time span to cover, and how to "
    "group events into eras"
)


def test_manifest_accepts_suggestion_hint():
    m = CreatorManifest(
        key="timelines",
        name="Timeline",
        version="1.0.0",
        sdk_compat=">=0.10,<1",
        emits=["flashcards.v1"],
        suggestion_hint=HINT,
    )
    assert m.suggestion_hint == HINT
    assert HINT in m.model_dump_json()


def test_manifest_without_suggestion_hint_still_validates():
    m = CreatorManifest(
        key="k", name="N", version="1.0.0", sdk_compat=">=0.1,<1", emits=["x"]
    )
    assert m.suggestion_hint is None


class _Config(BaseModel):
    n: int = 3


class _Creator(BaseCreator):
    config_model = _Config

    @property
    def manifest(self) -> CreatorManifest:
        return self.build_manifest(
            key="dummy",
            name="Dummy",
            version="0.1.0",
            sdk_compat=">=0.1,<1",
            emits=["flashcards.v1"],
            suggestion_hint="what to drill and where to focus difficulty",
        )

    async def generate(self, request):  # pragma: no cover - not exercised here
        raise NotImplementedError


def test_build_manifest_passes_through_suggestion_hint():
    m = _Creator().manifest
    assert m.suggestion_hint == "what to drill and where to focus difficulty"
    # still auto-derives config_schema alongside the new field
    assert m.config_schema["properties"]["n"]["default"] == 3
