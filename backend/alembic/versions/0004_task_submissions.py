"""Add task_submissions table.

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-24 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "task_submissions",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column(
            "firm_id",
            sa.Uuid(),
            sa.ForeignKey("firms.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("task_name", sa.String(100), nullable=False, index=True),
        sa.Column("args_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("kwargs_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=_NOW,
        ),
    )


def downgrade() -> None:
    pass
