"""profile

Revision ID: 0002_profile
Revises: 0001_initial
Create Date: 2025-12-19

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_profile"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profile",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("data_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("profile")



