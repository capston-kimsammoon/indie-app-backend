"""Add id column to stamp table (safe re-run)

Revision ID: 8bd4603eb81e
Revises: f65a67fd7cee
Create Date: 2025-09-21 13:48:49.548858
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "8bd4603eb81e"
down_revision: Union[str, None] = "f65a67fd7cee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with existence checks to avoid duplicate-column errors."""
    bind = op.get_bind()
    insp = inspect(bind)

    # 테이블 없으면 아무것도 하지 않음
    if not insp.has_table("stamp"):
        return

    # 현재 컬럼/인덱스/제약조건 목록
    existing_cols = {c["name"] for c in insp.get_columns("stamp")}
    existing_indexes = {i["name"] for i in insp.get_indexes("stamp")}
    existing_uniques = {
        c["name"] for c in insp.get_unique_constraints("stamp") if c.get("name")
    }

    # 1) id 컬럼 추가 (없을 때만)
    if "id" not in existing_cols:
        op.add_column("stamp", sa.Column("id", sa.Integer(), nullable=False))
    else:
        # 이미 있으면 nullable=False만 보장
        col = next((c for c in insp.get_columns("stamp") if c["name"] == "id"), None)
        if col and col.get("nullable", True):
            op.alter_column("stamp", "id", nullable=False)

    # 2) 인덱스 생성 (없을 때만)
    if "ix_stamp_id" not in existing_indexes:
        op.create_index(op.f("ix_stamp_id"), "stamp", ["id"], unique=False)

    # 3) 유니크 제약 생성 (없을 때만)
    if "unique_user_performance" not in existing_uniques:
        op.create_unique_constraint(
            "unique_user_performance", "stamp", ["user_id", "performance_id"]
        )


def downgrade() -> None:
    """Downgrade schema safely (drop only if exists)."""
    bind = op.get_bind()
    insp = inspect(bind)

    if not insp.has_table("stamp"):
        return

    existing_indexes = {i["name"] for i in insp.get_indexes("stamp")}
    existing_uniques = {
        c["name"] for c in insp.get_unique_constraints("stamp") if c.get("name")
    }
    existing_cols = {c["name"] for c in insp.get_columns("stamp")}

    # 유니크 제약 제거
    if "unique_user_performance" in existing_uniques:
        op.drop_constraint("unique_user_performance", "stamp", type_="unique")

    # 인덱스 제거
    if "ix_stamp_id" in existing_indexes:
        op.drop_index(op.f("ix_stamp_id"), table_name="stamp")

    # 컬럼 제거
    if "id" in existing_cols:
        op.drop_column("stamp", "id")
