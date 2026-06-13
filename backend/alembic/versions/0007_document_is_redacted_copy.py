"""Add is_redacted_copy column to documents table.

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-12 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column(
            "is_redacted_copy",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError(
        "Downgrade is not supported. "
        "This project enforces a fix-forward migration policy."
    )
