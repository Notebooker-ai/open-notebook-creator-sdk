"""open-notebook-creator-sdk: the normalized contract for Open Notebook creators.

Plugins depend on this package, subclass :class:`BaseCreator`, and expose the
subclass via the ``open_notebook.creators`` entry-point group.
"""

from __future__ import annotations

from .creator import BaseCreator, CreatorManifest, CreatorView, ModelRoleSpec
from .models import (
    ContentBundle,
    CreationError,
    CreationFile,
    CreationRequest,
    CreationResult,
    CreationStatus,
    ModelRole,
)
from .schemas import (
    SCHEMA_REGISTRY,
    get_schema,
    validate_artifact_data,
)

__version__ = "0.4.0"

#: Entry-point group plugins register under (used for dev discovery / warnings).
ENTRY_POINT_GROUP = "open_notebook.creators"

__all__ = [
    "__version__",
    "ENTRY_POINT_GROUP",
    # contract
    "BaseCreator",
    "CreatorManifest",
    "CreatorView",
    "ModelRoleSpec",
    # DTOs
    "ModelRole",
    "ContentBundle",
    "CreationFile",
    "CreationRequest",
    "CreationResult",
    "CreationError",
    "CreationStatus",
    # schemas
    "SCHEMA_REGISTRY",
    "get_schema",
    "validate_artifact_data",
]
