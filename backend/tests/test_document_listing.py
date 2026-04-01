"""Unit tests for document listing endpoint — filters, pagination, sorting."""

from __future__ import annotations

import uuid

import pytest
from shared.models.enums import (
    Classification,
    DocumentSource,
    IngestionStatus,
    Role,
)

from tests.conftest import FakeSession, api_client, auth_header, fake_with_docs
from tests.factories import make_document, make_user

_FIRM_ID = uuid.uuid4()
_MATTER_ID = uuid.uuid4()


class TestListDocumentsFilters:
    @pytest.mark.asyncio
    async def test_filter_by_ingestion_status(self) -> None:
        user = make_user(firm_id=_FIRM_ID, role=Role.admin)
        doc = make_document(
            firm_id=_FIRM_ID,
            matter_id=_MATTER_ID,
            uploaded_by=user.id,
            ingestion_status=IngestionStatus.failed,
        )
        fake = fake_with_docs([doc])

        async with api_client(user, fake) as ac:
            resp = await ac.get(
                "/documents/",
                params={"ingestion_status": "failed"},
                headers=auth_header(user),
            )

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["ingestion_status"] == "failed"

    @pytest.mark.asyncio
    async def test_filter_by_source(self) -> None:
        user = make_user(firm_id=_FIRM_ID, role=Role.admin)
        doc = make_document(
            firm_id=_FIRM_ID,
            matter_id=_MATTER_ID,
            uploaded_by=user.id,
            source=DocumentSource.government_production,
        )
        fake = fake_with_docs([doc])

        async with api_client(user, fake) as ac:
            resp = await ac.get(
                "/documents/",
                params={"source": "government_production"},
                headers=auth_header(user),
            )

        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1

    @pytest.mark.asyncio
    async def test_filter_by_classification(self) -> None:
        user = make_user(firm_id=_FIRM_ID, role=Role.admin)
        doc = make_document(
            firm_id=_FIRM_ID,
            matter_id=_MATTER_ID,
            uploaded_by=user.id,
            classification=Classification.brady,
        )
        fake = fake_with_docs([doc])

        async with api_client(user, fake) as ac:
            resp = await ac.get(
                "/documents/",
                params={"classification": "brady"},
                headers=auth_header(user),
            )

        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1

    @pytest.mark.asyncio
    async def test_filter_by_filename(self) -> None:
        user = make_user(firm_id=_FIRM_ID, role=Role.admin)
        doc = make_document(
            firm_id=_FIRM_ID,
            matter_id=_MATTER_ID,
            uploaded_by=user.id,
            filename="evidence_photo.jpg",
        )
        fake = fake_with_docs([doc])

        async with api_client(user, fake) as ac:
            resp = await ac.get(
                "/documents/",
                params={"filename": "evidence"},
                headers=auth_header(user),
            )

        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1


class TestListDocumentsPagination:
    @pytest.mark.asyncio
    async def test_pagination_offset_limit(self) -> None:
        user = make_user(firm_id=_FIRM_ID, role=Role.admin)
        doc = make_document(firm_id=_FIRM_ID, matter_id=_MATTER_ID, uploaded_by=user.id)
        # total=5 but only 1 doc in this page
        fake = fake_with_docs([doc], total=5)

        async with api_client(user, fake) as ac:
            resp = await ac.get(
                "/documents/",
                params={"offset": 2, "limit": 1},
                headers=auth_header(user),
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["offset"] == 2
        assert data["limit"] == 1
        assert data["total"] == 5

    @pytest.mark.asyncio
    async def test_default_pagination(self) -> None:
        user = make_user(firm_id=_FIRM_ID, role=Role.admin)
        fake = fake_with_docs([])

        async with api_client(user, fake) as ac:
            resp = await ac.get("/documents/", headers=auth_header(user))

        data = resp.json()
        assert data["offset"] == 0
        assert data["limit"] == 50

    @pytest.mark.asyncio
    async def test_limit_validation_max(self) -> None:
        user = make_user(firm_id=_FIRM_ID, role=Role.admin)
        fake = FakeSession()

        async with api_client(user, fake) as ac:
            resp = await ac.get(
                "/documents/",
                params={"limit": 999},
                headers=auth_header(user),
            )

        assert resp.status_code == 422


class TestListDocumentsSorting:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "sort_by", ["created_at", "filename", "size_bytes", "updated_at"]
    )
    async def test_valid_sort_fields(self, sort_by: str) -> None:
        user = make_user(firm_id=_FIRM_ID, role=Role.admin)
        fake = fake_with_docs([])

        async with api_client(user, fake) as ac:
            resp = await ac.get(
                "/documents/",
                params={"sort_by": sort_by},
                headers=auth_header(user),
            )

        assert resp.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize("sort_order", ["asc", "desc"])
    async def test_sort_order(self, sort_order: str) -> None:
        user = make_user(firm_id=_FIRM_ID, role=Role.admin)
        fake = fake_with_docs([])

        async with api_client(user, fake) as ac:
            resp = await ac.get(
                "/documents/",
                params={"sort_order": sort_order},
                headers=auth_header(user),
            )

        assert resp.status_code == 200
