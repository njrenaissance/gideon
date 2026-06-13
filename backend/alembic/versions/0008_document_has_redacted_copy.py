"""Replace is_redacted_copy with has_redacted_copy on documents table.

Switches from the two-record model (separate Document row per redacted copy)
to the sidecar model (redacted file lives alongside original in the same S3
folder; a single document record is updated in-place).

Revision ID: 0008
Revises: 0007
"""

import sqlalchemy as sa

from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column(
            "has_redacted_copy",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.drop_column("documents", "is_redacted_copy")


def downgrade() -> None:
    op.add_column(
        "documents",
        sa.Column(
            "is_redacted_copy",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.drop_column("documents", "has_redacted_copy")
