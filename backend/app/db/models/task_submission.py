"""TaskSubmission model — tracks tasks submitted via the API for firm-scoped queries."""

from __future__ import annotations

import uuid
from datetime import datetime

from shared.models.enums import TaskState
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TaskSubmission(Base):
    __tablename__ = "task_submissions"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    firm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("firms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    task_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    args_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    kwargs_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TaskState.pending
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
