"""Unit tests for SDK task methods.

Uses httpx.MockTransport following the pattern in test_entity_methods.py.
"""

from __future__ import annotations

import json
import uuid

import httpx
from shared.models.base import MessageResponse
from shared.models.task import TaskResponse, TaskSubmitResponse, TaskSummary

from tests.conftest import build_authenticated_client

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FIRM_ID = str(uuid.uuid4())
_USER_ID = str(uuid.uuid4())
_TASK_ID = str(uuid.uuid4())
_NOW = "2025-01-01T00:00:00+00:00"


def _task_summary_json(tid: str | None = None) -> dict:
    return {
        "id": tid or _TASK_ID,
        "task_name": "ping",
        "status": "PENDING",
        "submitted_at": _NOW,
        "submitted_by": _USER_ID,
    }


def _task_response_json(tid: str | None = None) -> dict:
    return {
        **_task_summary_json(tid),
        "firm_id": _FIRM_ID,
        "args": [],
        "kwargs": {},
        "result": None,
        "date_done": None,
        "traceback": None,
    }


# ---------------------------------------------------------------------------
# list_tasks
# ---------------------------------------------------------------------------


def test_list_tasks() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/tasks/"
        return httpx.Response(200, json=[_task_summary_json()])

    client = build_authenticated_client(handler)
    result = client.list_tasks()
    assert len(result) == 1
    assert isinstance(result[0], TaskSummary)
    assert result[0].task_name == "ping"


def test_list_tasks_with_filters() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["status"] == "SUCCESS"
        assert request.url.params["task_name"] == "ping"
        return httpx.Response(200, json=[])

    client = build_authenticated_client(handler)
    result = client.list_tasks(status="SUCCESS", task_name="ping")
    assert result == []


# ---------------------------------------------------------------------------
# get_task
# ---------------------------------------------------------------------------


def test_get_task() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert f"/tasks/{_TASK_ID}" == request.url.path
        return httpx.Response(200, json=_task_response_json())

    client = build_authenticated_client(handler)
    result = client.get_task(_TASK_ID)
    assert isinstance(result, TaskResponse)
    assert result.task_name == "ping"


# ---------------------------------------------------------------------------
# submit_task
# ---------------------------------------------------------------------------


def test_submit_task() -> None:
    sent_body: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/tasks/"
        assert request.method == "POST"
        sent_body.update(json.loads(request.content))
        return httpx.Response(201, json={"task_id": _TASK_ID})

    client = build_authenticated_client(handler)
    result = client.submit_task(task_name="ping")
    assert isinstance(result, TaskSubmitResponse)
    assert result.task_id == _TASK_ID
    assert sent_body["task_name"] == "ping"


def test_submit_task_with_args() -> None:
    sent_body: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        sent_body.update(json.loads(request.content))
        return httpx.Response(201, json={"task_id": _TASK_ID})

    client = build_authenticated_client(handler)
    client.submit_task(task_name="ping", args=[1, 2], kwargs={"key": "val"})
    assert sent_body["args"] == [1, 2]
    assert sent_body["kwargs"] == {"key": "val"}


# ---------------------------------------------------------------------------
# cancel_task
# ---------------------------------------------------------------------------


def test_cancel_task() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "DELETE"
        assert f"/tasks/{_TASK_ID}" == request.url.path
        return httpx.Response(200, json={"detail": "Task revoked"})

    client = build_authenticated_client(handler)
    result = client.cancel_task(_TASK_ID)
    assert isinstance(result, MessageResponse)
    assert result.detail == "Task revoked"
