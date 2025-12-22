"""variant_items

Revision ID: 0003_variant_items
Revises: 0002_profile
Create Date: 2025-12-22

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003_variant_items"
down_revision = "0002_profile"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "variant_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("variant_id", sa.String(), sa.ForeignKey("variants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("section", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("entry_id", sa.String(), sa.ForeignKey("entries.id", ondelete="CASCADE"), nullable=False),
    )
    # Create an index for efficient lookups
    op.create_index("ix_variant_items_variant_section", "variant_items", ["variant_id", "section"])


def downgrade() -> None:
    op.drop_index("ix_variant_items_variant_section", table_name="variant_items")
    op.drop_table("variant_items")

