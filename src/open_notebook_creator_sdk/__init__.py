"""open-notebook-creator-sdk: the normalized contract for Open Notebook creators.

Plugins depend on this package, subclass :class:`BaseCreator`, and expose the
result via the ``open_notebook.creators`` entry point group. The host builds a
:class:`CreationRequest`, the creator returns a :class:`CreationResult`, and the
``data`` payload validates against an immutable schema in :mod:`.schemas`.
"""

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

#: Entry-point group creator packages register under.
ENTRY_POINT_GROUP = "open_notebook.creators"

__version__ = "0.7.0"

__all__ = [
    "BaseCreator",
    "CreatorManifest",
    "CreatorView",
    "ModelRoleSpec",
    "ContentBundle",
    "CreationError",
    "CreationFile",
    "CreationRequest",
    "CreationResult",
    "CreationStatus",
    "ModelRole",
    "ENTRY_POINT_GROUP",
    "__version__",
]
