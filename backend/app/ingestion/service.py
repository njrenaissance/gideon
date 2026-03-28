"""Stub ingestion workflow — placeholder for the full pipeline.

Future features will extend this with:
- Text extraction via Apache Tika + Tesseract OCR
- Chunking and overlap strategy
- Embedding via Ollama (nomic-embed-text)
- Vector storage in Qdrant with permission payload
"""

from __future__ import annotations

import logging
import uuid

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates the document ingestion pipeline.

    Currently a stub that logs the request. The full pipeline will
    download from S3, extract text, chunk, embed, and store vectors.
    """

    async def process_document(self, document_id: uuid.UUID, s3_key: str) -> None:
        """Kick off ingestion for a newly uploaded document.

        Args:
            document_id: The document's primary key.
            s3_key: The S3 object key where the original file is stored.
        """
        logger.info(
            "Ingestion stub: document_id=%s s3_key=%s (pipeline not yet implemented)",
            document_id,
            s3_key,
        )
