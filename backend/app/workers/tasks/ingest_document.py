"""Stub Celery task for document ingestion.

Future: downloads from S3, runs Tika text extraction, chunks, embeds
via Ollama, and stores vectors in Qdrant.
"""

from __future__ import annotations

import logging

from celery import shared_task  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


@shared_task(name="opencase.ingest_document")  # type: ignore[untyped-decorator]
def ingest_document(document_id: str, s3_key: str) -> dict[str, str]:
    """Ingest a document — stub implementation.

    Args:
        document_id: UUID string of the document record.
        s3_key: S3 object key where the original file is stored.

    Returns:
        Status dict with ``{"status": "stub", "document_id": ...}``.
    """
    logger.info("ingest_document stub: %s at %s", document_id, s3_key)
    return {"status": "stub", "document_id": document_id}
