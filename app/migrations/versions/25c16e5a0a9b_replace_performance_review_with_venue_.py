"""replace performance-review with venue-review

Revision ID: 25c16e5a0a9b
Revises: c8737f8636ab
Create Date: 2025-09-15 22:41:56.106672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25c16e5a0a9b'
down_revision: Union[str, None] = 'c8737f8636ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1) 예전 리뷰 테이블들 제거(존재 시만)
    op.execute("DROP TABLE IF EXISTS review_like")
    op.execute("DROP TABLE IF EXISTS review_image")
    op.execute("DROP TABLE IF EXISTS review")

    # 2) 공연장 리뷰(review) 테이블 생성
    op.create_table(
        "review",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("venue_id", sa.Integer(),
                  sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(),
                  server_default=sa.func.now(), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_review_id", "review", ["id"])


def downgrade() -> None:
    # 되돌릴 때: 방금 만든 것만 제거(필요 최소한)
    op.drop_index("ix_review_id", table_name="review")
    op.drop_table("review")
