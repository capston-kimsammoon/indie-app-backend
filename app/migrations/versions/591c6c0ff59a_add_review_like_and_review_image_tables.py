"""add review_like and review_image tables (safe)

Revision ID: 591c6c0ff59a
Revises: f3415a3ab6c7
Create Date: 2025-09-24 19:13:55.748645
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "591c6c0ff59a"
down_revision: Union[str, None] = "f3415a3ab6c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Only create the new review tables if missing. Do NOT touch stamp indexes."""
    bind = op.get_bind()
    insp = inspect(bind)

    # review_like
    if not insp.has_table("review_like"):
        op.create_table(
            "review_like",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
            sa.Column("review_id", sa.Integer(), sa.ForeignKey("review.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
            sa.UniqueConstraint("review_id", "user_id", name="uq_review_like_review_user"),
        )
        op.create_index("ix_review_like_review_id", "review_like", ["review_id"], unique=False)
        op.create_index("ix_review_like_user_id", "review_like", ["user_id"], unique=False)

    # review_image
    if not insp.has_table("review_image"):
        op.create_table(
            "review_image",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
            sa.Column("review_id", sa.Integer(), sa.ForeignKey("review.id", ondelete="CASCADE"), nullable=False),
            sa.Column("image_url", sa.String(500), nullable=False),
        )
        op.create_index("ix_review_image_review_id", "review_image", ["review_id"], unique=False)


def downgrade() -> None:
    """Drop only what we created, and guard each drop."""
    bind = op.get_bind()
    insp = inspect(bind)

    if insp.has_table("review_image"):
        try:
            op.drop_index("ix_review_image_review_id", table_name="review_image")
        except Exception:
            pass
        op.drop_table("review_image")

    if insp.has_table("review_like"):
        try:
            op.drop_index("ix_review_like_user_id", table_name="review_like")
        except Exception:
            pass
        try:
            op.drop_index("ix_review_like_review_id", table_name="review_like")
        except Exception:
            pass
        try:
            op.drop_constraint("uq_review_like_review_user", "review_like", type_="unique")
        except Exception:
            pass
        op.drop_table("review_like")
