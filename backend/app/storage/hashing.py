"""Chunked SHA-256 hashing for uploaded files with size enforcement."""

from __future__ import annotations

import hashlib
from io import BytesIO

from fastapi import UploadFile

_CHUNK_SIZE = 64 * 1024  # 64 KB
_MAX_UPLOAD_BYTES = 100 * 1024 * 1024  # 100 MB


class FileTooLargeError(Exception):
    """Raised when an uploaded file exceeds the size limit."""


async def read_and_hash(
    upload_file: UploadFile,
    *,
    max_bytes: int = _MAX_UPLOAD_BYTES,
) -> tuple[BytesIO, str, int]:
    """Read an ``UploadFile`` in chunks, compute its SHA-256, and enforce a size limit.

    Returns:
        A tuple of ``(data, hex_digest, size_bytes)`` where *data* is a
        :class:`~io.BytesIO` seeked to position 0.

    Raises:
        FileTooLargeError: If the file exceeds *max_bytes*.
    """
    hasher = hashlib.sha256()
    buf = BytesIO()
    total = 0

    while chunk := await upload_file.read(_CHUNK_SIZE):
        total += len(chunk)
        if total > max_bytes:
            raise FileTooLargeError(
                f"File exceeds maximum allowed size of {max_bytes} bytes"
            )
        hasher.update(chunk)
        buf.write(chunk)

    buf.seek(0)
    return buf, hasher.hexdigest(), total
