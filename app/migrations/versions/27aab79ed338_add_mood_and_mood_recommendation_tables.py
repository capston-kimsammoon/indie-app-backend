"""add mood and mood_recommendation tables

Revision ID: 27aab79ed338
Revises: 3241115bce5f
Create Date: 2025-09-22 13:57:36.874583
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "27aab79ed338"
down_revision: Union[str, None] = "3241115bce5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # --- mood ---
    op.create_table(
        "mood",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    # (선택) PK 컬럼 id에 대한 별도 인덱스는 불필요하므로 생성하지 않음
    # op.create_index(op.f("ix_mood_id"), "mood", ["id"], unique=False)

    # --- mood_recommendation ---
    op.create_table(
        "mood_recommendation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mood_id", sa.Integer(), nullable=False),
        sa.Column("performance_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["mood_id"], ["mood.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["performance_id"], ["performance.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mood_id", "performance_id", name="uq_mood_performance"),
    )
    op.create_index(
        "ix_mood_id_created_at",
        "mood_recommendation",
        ["mood_id", "created_at"],
        unique=False,
    )

    # ❌ 절대 건드리면 안 됨 (FK 이유): stamp 인덱스 드롭/생성 금지
    # op.drop_index(op.f("ix_stamp_performance_id"), table_name="stamp")
    # op.drop_index(op.f("ix_stamp_user_id"), table_name="stamp")
    # op.create_index(op.f("ix_stamp_id"), "stamp", ["id"], unique=False)

    # (권장) 관련 없는 magazine_block 인덱스 드롭도 제거
    # op.drop_index(op.f("ix_magazine_block_id"), table_name="magazine_block")
    # op.drop_index(op.f("ix_magazine_block_magazine_id_order"), table_name="magazine_block")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_mood_id_created_at", table_name="mood_recommendation")
    op.drop_table("mood_recommendation")

    # (선택) 위에서 안 만든 인덱스는 되돌릴 필요 없음
    # op.drop_index(op.f("ix_mood_id"), table_name="mood")
    op.drop_table("mood")
