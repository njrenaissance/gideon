"""Storage module — S3-compatible object storage via MinIO."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.storage.s3 import S3StorageService

_service: S3StorageService | None = None


def get_storage_service() -> S3StorageService:
    """FastAPI dependency returning the S3StorageService singleton."""
    global _service  # noqa: PLW0603
    if _service is None:
        from app.core.config import settings
        from app.storage.s3 import S3StorageService

        _service = S3StorageService(settings.s3)
    return _service
