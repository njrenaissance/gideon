"""Celery task for document redaction — sidecar model.

Downloads the original file from S3, replaces configured keywords with
deterministic placeholders, scrubs document metadata, then uploads the
result as ``redacted.{ext}`` alongside the original in the same S3 folder.
The original Document DB record is updated in-place (``has_redacted_copy``
flag set to True); no new Document row is created.

The task finishes by dispatching ``gideon.ingest_document`` for the same
document_id, passing the redacted S3 key so extraction targets the clean
copy rather than the original.

Pipeline integration
--------------------
``gideon.ingest_document`` auto-dispatches this task for documents where
``has_redacted_copy=False`` and ``settings.redaction.enabled`` is True.
"""

from __future__ import annotations

import asyncio
import logging

from celery import shared_task  # type: ignore[import-untyped]
from opentelemetry import trace
from opentelemetry.trace import StatusCode
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.storage.s3 import S3StorageService

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

_PDF_MIME = "application/pdf"
_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@shared_task(  # type: ignore[untyped-decorator]
    name="gideon.redact_document",
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True,
)
def redact_document(document_id: str, s3_key: str) -> dict[str, object]:
    """Redact a document and save the result as a sidecar file.

    Args:
        document_id: UUID string of the document record.
        s3_key: S3 object key of the original file.

    Returns:
        Status dict describing the outcome.
    """
    logger.info("redact_document: %s at %s", document_id, s3_key)
    return asyncio.run(_redact(document_id, s3_key))


async def _redact(document_id: str, s3_key: str) -> dict[str, object]:
    with tracer.start_as_current_span(
        "redact_document",
        record_exception=False,
        attributes={
            "document.id": document_id,
            "document.s3_key": s3_key,
        },
    ) as span:
        try:
            return await _run_redact(document_id, s3_key, span)
        except Exception as exc:
            span.set_status(StatusCode.ERROR, str(exc))
            span.record_exception(exc)
            raise


async def _load_original_document(document_id: str) -> dict[str, object]:
    """Verify the document exists and return basic fields for logging."""
    from app.db.models.document import Document

    engine = create_async_engine(settings.db.url, pool_pre_ping=True)
    try:
        async with AsyncSession(engine) as session:
            doc = await session.get(Document, document_id)
            if doc is None:
                msg = f"Document {document_id} not found"
                raise ValueError(msg)
            return {
                "firm_id": str(doc.firm_id),
                "matter_id": str(doc.matter_id),
                "filename": doc.filename,
            }
    finally:
        await engine.dispose()


async def _update_has_redacted_copy(document_id: str) -> None:
    """Set has_redacted_copy=True on the document record."""
    from app.db.models.document import Document

    engine = create_async_engine(settings.db.url, pool_pre_ping=True)
    try:
        async with AsyncSession(engine) as session:
            doc = await session.get(Document, document_id)
            if doc is None:
                logger.warning(
                    "_update_has_redacted_copy: document %s not found", document_id
                )
                return
            doc.has_redacted_copy = True
            await session.commit()
    finally:
        await engine.dispose()


async def _run_redact(
    document_id: str,
    s3_key: str,
    span: trace.Span,
) -> dict[str, object]:
    # 1. Check keywords — skip immediately if none configured
    keywords = settings.redaction.keywords
    if not keywords:
        logger.info("redact_document: no keywords configured, skipping %s", document_id)
        span.set_attribute("redaction.skipped", True)
        span.set_attribute("redaction.skip_reason", "no_keywords_configured")
        return {"status": "skipped", "reason": "no_keywords_configured"}

    # 2. Verify document exists in DB
    with tracer.start_as_current_span("redaction.db_lookup"):
        try:
            orig = await _load_original_document(document_id)
        except ValueError:
            logger.warning(
                "redact_document: document %s not found in DB — skipping",
                document_id,
            )
            span.set_attribute("redaction.skipped", True)
            span.set_attribute("redaction.skip_reason", "document_not_found")
            return {"status": "skipped", "reason": "document_not_found"}

    # 3. Download original
    from app.storage import get_storage_service

    storage = get_storage_service()
    with tracer.start_as_current_span("redaction.s3_download"):
        file_bytes, content_type = await storage.download_document(s3_key)

    # 4. Guard: PDF and DOCX only (.doc requires LibreOffice — see roadmap)
    if content_type not in (_PDF_MIME, _DOCX_MIME):
        logger.warning(
            "redact_document: unsupported format %r for %s — skipping",
            content_type,
            document_id,
        )
        span.set_attribute("redaction.skipped", True)
        span.set_attribute("redaction.skip_reason", "unsupported_format")
        return {"status": "skipped", "reason": "unsupported_format"}

    # 5. Build keyword map and run format-specific redaction
    from app.redaction import get_redaction_service

    redaction = get_redaction_service()
    keyword_map = redaction.build_keyword_map(keywords)

    if content_type == _PDF_MIME:
        with tracer.start_as_current_span("redaction.redact"):
            redacted_bytes, occurrence_counts, orig_metadata = redaction.redact_pdf(
                file_bytes, keyword_map
            )
        extension = "pdf"
        redacted_content_type = _PDF_MIME
    else:
        with tracer.start_as_current_span("redaction.redact"):
            redacted_bytes, occurrence_counts, orig_metadata = redaction.redact_docx(
                file_bytes, keyword_map
            )
        extension = "docx"
        redacted_content_type = _DOCX_MIME

    total_replacements = sum(occurrence_counts.values())
    span.set_attribute("redaction.keyword_count", len(keyword_map))
    span.set_attribute("redaction.total_replacements", total_replacements)

    # 6. Upload sidecar alongside the original: {prefix}/redacted.{ext}
    s3_prefix = s3_key.rsplit("/", 1)[0]
    redacted_s3_key = S3StorageService.redacted_object_key(s3_prefix, extension)
    manifest_key = S3StorageService.redacted_manifest_key(s3_prefix)

    keyword_replacements = [
        {
            "original": orig_kw,
            "placeholder": ph,
            "occurrence_count": occurrence_counts.get(ph, 0),
        }
        for orig_kw, ph in keyword_map.items()
    ]
    manifest: dict[str, object] = {
        "original_document_id": document_id,
        "original_filename": orig["filename"],
        "metadata_removed": orig_metadata,
        "keyword_replacements": keyword_replacements,
        "total_replacements": total_replacements,
    }

    with tracer.start_as_current_span("redaction.s3_upload"):
        await storage.upload_bytes(
            key=redacted_s3_key,
            data=redacted_bytes,
            content_type=redacted_content_type,
        )
        await storage.upload_json(key=manifest_key, data=manifest)

    span.set_attribute("redaction.redacted_s3_key", redacted_s3_key)
    span.set_attribute("redaction.manifest_key", manifest_key)

    # 7. Mark the document record so ingest knows to use the sidecar
    with tracer.start_as_current_span("redaction.db_update"):
        await _update_has_redacted_copy(document_id)

    # 8. Dispatch ingestion for the same document, passing the redacted key
    from app.workers import celery_app

    celery_app.send_task("gideon.ingest_document", args=[document_id, redacted_s3_key])
    logger.info(
        "redact_document done: %s → %s (%d replacements) — ingesting",
        document_id,
        redacted_s3_key,
        total_replacements,
    )

    return {
        "status": "completed",
        "original_document_id": document_id,
        "redacted_s3_key": redacted_s3_key,
        "manifest_key": manifest_key,
        "keyword_count": len(keyword_map),
        "total_replacements": total_replacements,
    }
