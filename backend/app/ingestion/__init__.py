"""Ingestion module — document processing pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ingestion.service import IngestionService

_service: IngestionService | None = None


def get_ingestion_service() -> IngestionService:
    """FastAPI dependency returning the IngestionService singleton."""
    global _service  # noqa: PLW0603
    if _service is None:
        from app.ingestion.service import IngestionService

        _service = IngestionService()
    return _service
