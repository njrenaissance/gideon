"""TaskBroker — thin abstraction over Celery for submit, status, and revoke.

Keeps the FastAPI layer decoupled from Celery internals so the background
job backend can be swapped in the future without touching the API router.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from celery import Celery  # type: ignore[import-untyped]

from app.workers import celery_app


@dataclass(frozen=True)
class TaskStatusResult:
    """Snapshot of a task's current state from the result backend."""

    state: str
    result: Any | None
    date_done: datetime | None
    traceback: str | None


class TaskBroker:
    """Wraps Celery send_task / AsyncResult / control.revoke."""

    def __init__(self, celery: Celery) -> None:
        self._celery = celery

    def submit(
        self, celery_task_name: str, args: list[Any], kwargs: dict[str, Any]
    ) -> str:
        """Submit a task and return its ID."""
        result = self._celery.send_task(celery_task_name, args=args, kwargs=kwargs)
        return str(result.id)

    def get_status(self, task_id: str) -> TaskStatusResult:
        """Query the result backend for live task state."""
        r = self._celery.AsyncResult(task_id)
        return TaskStatusResult(
            state=r.state,
            result=r.result,
            date_done=getattr(r, "date_done", None),
            traceback=r.traceback,
        )

    def revoke(self, task_id: str, *, terminate: bool = False) -> None:
        """Revoke (cancel) a pending or running task."""
        self._celery.control.revoke(task_id, terminate=terminate)


# Singleton — shared across all requests.
_broker = TaskBroker(celery_app)


def get_task_broker() -> TaskBroker:
    """FastAPI dependency returning the TaskBroker singleton."""
    return _broker
