"""The post-generation editing contract: file roles, RenderRequest/SourceDoc,
BaseCreator.render, and the manifest's editable_source flag."""

from __future__ import annotations

import asyncio

import pytest
from pydantic import BaseModel

from open_notebook_creator_sdk import (
    BaseCreator,
    CreationFile,
    CreationRequest,
    CreationResult,
    CreatorManifest,
    RenderRequest,
    SourceDoc,
)


def test_creation_file_role_defaults_to_output():
    f = CreationFile(filename="a.html", content_type="text/html", path="a.html")
    assert f.role == "output"
    # Pre-role dumps (no `role` key) still load as outputs.
    assert CreationFile.model_validate(
        {"filename": "a.html", "content_type": "text/html", "path": "a.html"}
    ).role == "output"


def test_creation_file_accepts_source_and_asset_roles():
    src = CreationFile(
        filename="doc.qmd", content_type="text/markdown", path="doc.qmd", role="source"
    )
    asset = CreationFile(
        filename="fig.svg", content_type="image/svg+xml", path="fig.svg", role="asset"
    )
    assert src.role == "source" and asset.role == "asset"
    with pytest.raises(Exception):
        CreationFile(filename="x", content_type="t", path="x", role="bogus")


def test_render_request_roundtrip():
    req = RenderRequest(
        sources=[SourceDoc(filename="doc.qmd", content_type="text/markdown", content="# Hi")],
        config={"formats": ["html"]},
        data={"title": "T"},
        output_dir="/tmp/x",
        artifact_id="a1",
    )
    assert req.sources[0].content == "# Hi"
    assert req.language is None and req.user_id is None


def test_manifest_editable_source_defaults_false():
    m = CreatorManifest(
        key="k", name="N", version="1.0.0", sdk_compat=">=0.1,<1", emits=["x"]
    )
    assert m.editable_source is False


class _Cfg(BaseModel):
    n: int = 1


class _NoRender(BaseCreator):
    config_model = _Cfg

    @property
    def manifest(self):
        return self.build_manifest(
            key="k", name="N", version="1.0.0", sdk_compat=">=0.1,<1", emits=["x"]
        )

    async def generate(self, request: CreationRequest) -> CreationResult:
        return CreationResult(status="SUCCESS", schema_id="x")


class _WithRender(_NoRender):
    @property
    def manifest(self):
        return self.build_manifest(
            key="k",
            name="N",
            version="1.0.0",
            sdk_compat=">=0.1,<1",
            emits=["x"],
            editable_source=True,
        )

    async def render(self, request: RenderRequest) -> CreationResult:
        return CreationResult(
            status="SUCCESS",
            schema_id="x",
            data={**request.data, "rendered_from": request.sources[0].content},
        )


def _req():
    return RenderRequest(
        sources=[SourceDoc(filename="s", content_type="text/plain", content="edited")],
        data={"title": "T"},
        output_dir="/tmp",
        artifact_id="a",
    )


def test_render_default_is_unsupported():
    loop = asyncio.new_event_loop()
    with pytest.raises(NotImplementedError):
        loop.run_until_complete(_NoRender().render(_req()))


def test_render_override_receives_sources_and_previous_data():
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(_WithRender().render(_req()))
    assert result.data == {"title": "T", "rendered_from": "edited"}
    assert _WithRender().manifest.editable_source is True
