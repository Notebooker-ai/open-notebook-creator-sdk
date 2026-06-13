"""Compliance suite plugin authors run against their creator.

Usage in a plugin repo's tests::

    from open_notebook_creator_sdk.testing import assert_creator_compliant
    from my_creator import MyCreator

    def test_compliance():
        assert_creator_compliant(MyCreator())

For an end-to-end ``generate`` check, use :func:`assert_generate_compliant` with a
stubbed model factory.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from . import __version__
from .creator import BaseCreator
from .models import ContentBundle, CreationRequest, CreationResult
from .schemas import SCHEMA_REGISTRY, validate_artifact_data


def assert_creator_compliant(creator: BaseCreator) -> None:
    """Static checks: manifest validity, sdk_compat, schema ids, config model,
    role specs. Does not call ``generate``."""
    m = creator.manifest

    assert m.key, "manifest.key must be non-empty"
    assert m.name, "manifest.name must be non-empty"
    assert m.version, "manifest.version must be non-empty"

    # sdk_compat must be a valid specifier and satisfied by the installed SDK
    spec = SpecifierSet(m.sdk_compat)
    assert Version(__version__) in spec, (
        f"installed SDK {__version__} does not satisfy creator sdk_compat "
        f"'{m.sdk_compat}'"
    )

    assert m.emits, "manifest.emits must list at least one schema id"
    for sid in m.emits:
        assert sid in SCHEMA_REGISTRY, f"emitted schema '{sid}' not in SCHEMA_REGISTRY"

    assert isinstance(m.config_schema, dict) and m.config_schema, (
        "manifest.config_schema must be a non-empty JSON Schema"
    )
    assert hasattr(creator, "config_model"), "creator.config_model is required"

    role_keys = [r.key for r in m.model_roles]
    assert len(role_keys) == len(set(role_keys)), "duplicate model_role keys"
    for r in m.model_roles:
        assert r.kind, f"model_role '{r.key}' missing kind"


def _check_no_credential_leak(request: CreationRequest) -> None:
    dumped = request.model_dump_json()
    for role in request.models.values():
        for v in role.config.values():
            if isinstance(v, str) and v:
                assert v not in dumped, (
                    "credential material leaked into CreationRequest serialization"
                )


def assert_result_compliant(creator: BaseCreator, result: CreationResult) -> None:
    assert result.schema_id in creator.manifest.emits, (
        f"result.schema_id '{result.schema_id}' not in manifest.emits"
    )
    # data must validate against the declared schema
    validate_artifact_data(result.schema_id, result.data)
    # data must be JSON-serializable
    json.dumps(result.data)
    # file paths must be relative and contained
    for f in result.files:
        assert not f.path.startswith("/"), f"file path must be relative: {f.path}"
        assert ".." not in f.path.split("/"), f"file path escapes output_dir: {f.path}"


def assert_generate_compliant(
    creator: BaseCreator,
    *,
    output_dir: str,
    config: Optional[Dict[str, Any]] = None,
    models: Optional[Dict[str, Any]] = None,
    content: str = "Sample notebook content for compliance testing.",
) -> CreationResult:
    """Run ``generate`` once with a built request and assert the result complies.

    Pass ``models`` mapping each declared role key to a (possibly stubbed)
    ``ModelRole``. Returns the result for further assertions.
    """
    assert_creator_compliant(creator)

    request = CreationRequest(
        content=ContentBundle(text=content, token_count=len(content.split())),
        config=config or {},
        models=models or {},
        output_dir=output_dir,
        artifact_id="compliance-test-artifact",
    )
    _check_no_credential_leak(request)

    result = asyncio.get_event_loop().run_until_complete(creator.generate(request))
    assert isinstance(result, CreationResult)
    assert_result_compliant(creator, result)
    return result
