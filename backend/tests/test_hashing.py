"""Unit tests for app.storage.hashing — chunked SHA-256 with size enforcement."""

from __future__ import annotations

import hashlib
from io import BytesIO
from unittest.mock import AsyncMock

import pytest

from app.storage.hashing import FileTooLargeError, read_and_hash


def _make_upload_file(content: bytes) -> AsyncMock:
    """Create a mock UploadFile backed by a BytesIO."""
    buf = BytesIO(content)

    mock = AsyncMock()

    async def _read(size: int = -1) -> bytes:
        return buf.read(size)

    mock.read = _read
    return mock


class TestReadAndHash:
    @pytest.mark.asyncio
    async def test_computes_correct_sha256(self) -> None:
        content = b"the quick brown fox jumps over the lazy dog"
        expected = hashlib.sha256(content).hexdigest()

        upload = _make_upload_file(content)
        data, digest, size = await read_and_hash(upload)

        assert digest == expected
        assert size == len(content)

    @pytest.mark.asyncio
    async def test_returns_bytesio_seeked_to_zero(self) -> None:
        content = b"some file content"
        upload = _make_upload_file(content)

        data, _digest, _size = await read_and_hash(upload)

        assert data.tell() == 0
        assert data.read() == content

    @pytest.mark.asyncio
    async def test_enforces_size_limit(self) -> None:
        max_bytes = 100
        content = b"x" * (max_bytes + 1)
        upload = _make_upload_file(content)

        with pytest.raises(FileTooLargeError):
            await read_and_hash(upload, max_bytes=max_bytes)

    @pytest.mark.asyncio
    async def test_allows_exact_size_limit(self) -> None:
        max_bytes = 100
        content = b"x" * max_bytes
        upload = _make_upload_file(content)

        data, digest, size = await read_and_hash(upload, max_bytes=max_bytes)
        assert size == max_bytes

    @pytest.mark.asyncio
    async def test_empty_file(self) -> None:
        content = b""
        expected = hashlib.sha256(content).hexdigest()
        upload = _make_upload_file(content)

        data, digest, size = await read_and_hash(upload)

        assert digest == expected
        assert size == 0
        assert data.read() == b""
