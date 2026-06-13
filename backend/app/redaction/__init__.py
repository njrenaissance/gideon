"""Redaction module — keyword replacement and metadata scrubbing."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.redaction.service import RedactionService

_service: RedactionService | None = None


def get_redaction_service() -> RedactionService:
    """Return the RedactionService singleton."""
    global _service  # noqa: PLW0603
    if _service is None:
        from app.redaction.service import RedactionService

        _service = RedactionService()
    return _service
