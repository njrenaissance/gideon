"""Pydantic request/response models for document endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from shared.models.enums import Classification, DocumentSource

# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------


class DocumentSummary(BaseModel):
    """Lightweight document reference (for lists)."""

    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    source: DocumentSource
    classification: Classification
    legal_hold: bool
    matter_id: UUID


class DocumentResponse(DocumentSummary):
    """Full document detail (single-document endpoint)."""

    firm_id: UUID
    file_hash: str
    bates_number: str | None
    uploaded_by: UUID
    created_at: datetime
    updated_at: datetime
