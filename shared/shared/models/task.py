"""Pydantic request/response models for task endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from shared.models.enums import TaskState

# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------


class TaskSubmitResponse(BaseModel):
    """Returned after submitting a task."""

    task_id: str


class TaskSummary(BaseModel):
    """Lightweight task reference (for lists)."""

    id: str
    task_name: str
    status: TaskState
    submitted_at: datetime
    submitted_by: UUID


class TaskResponse(TaskSummary):
    """Full task detail (single-task endpoint)."""

    firm_id: UUID
    args: list[Any]
    kwargs: dict[str, Any]
    result: Any | None = None
    date_done: datetime | None = None
    traceback: str | None = None


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------


class SubmitTaskRequest(BaseModel):
    task_name: str = Field(min_length=1, max_length=100)
    args: list[Any] = Field(default_factory=list)
    kwargs: dict[str, Any] = Field(default_factory=dict)


class UpdateTaskRequest(BaseModel):
    """Scaffold — no fields are updatable yet."""
