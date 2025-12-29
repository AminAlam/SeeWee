"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-12-19

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "entries",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("type", sa.String(), nullable=False, index=True),
        sa.Column("data_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "entry_tags",
        sa.Column("entry_id", sa.String(), sa.ForeignKey("entries.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag", sa.String(), primary_key=True),
    )

    op.create_table(
        "variants",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("rules_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "variant_sections",
        sa.Column("variant_id", sa.String(), sa.ForeignKey("variants.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("section", sa.String(), primary_key=True),
        sa.Column("position", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("variant_sections")
    op.drop_table("variants")
    op.drop_table("entry_tags")
    op.drop_table("entries")



