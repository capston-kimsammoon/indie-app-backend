"""stamp: add id column as primary key and unique(user_id, performance_id)

Revision ID: 3241115bce5f
Revises: a6f0a9484740
Create Date: 2025-09-21 15:07:22.153323
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3241115bce5f"
down_revision: Union[str, None] = "a6f0a9484740"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    MySQL safe path:
      0) (FK 보호용) 보조 인덱스 선추가(user_id, performance_id)
      1) id 컬럼 NULL 허용으로 추가
      2) 기존 행 id 백필
      3) 기존 복합 PK(user_id, performance_id) 드롭
      4) id NOT NULL + AUTO_INCREMENT + PK로 확정
      5) UNIQUE(user_id, performance_id) 추가
    """

    # 0) FK 제약 보호용 보조 인덱스
    op.create_index("ix_stamp_user_id", "stamp", ["user_id"], unique=False)
    op.create_index("ix_stamp_performance_id", "stamp", ["performance_id"], unique=False)

    # 1) id 컬럼 추가 (우선 NULL 허용)
    op.add_column("stamp", sa.Column("id", sa.Integer(), nullable=True))

    # 2) 기존 레코드에 순번 채워넣기 (MySQL)
    op.execute("SET @i := 0;")
    op.execute(
        """
        UPDATE `stamp`
        SET `id` = (@i := @i + 1)
        ORDER BY `user_id`, `performance_id`, `created_at`;
        """
    )

    # 3) 기존 복합 PK 제거
    op.execute("ALTER TABLE `stamp` DROP PRIMARY KEY;")

    # 4) id를 PK + AUTO_INCREMENT로 확정
    op.execute(
        """
        ALTER TABLE `stamp`
        MODIFY COLUMN `id` INT NOT NULL AUTO_INCREMENT,
        ADD PRIMARY KEY (`id`);
        """
    )

    # 5) (user_id, performance_id) 중복 방지 유니크 인덱스
    op.execute(
        """
        CREATE UNIQUE INDEX `unique_user_performance`
        ON `stamp`(`user_id`, `performance_id`);
        """
    )


def downgrade() -> None:
    """
    Reverse:
      1) UNIQUE(user_id, performance_id) 제거
      2) PK(id) 제거
      3) id 컬럼 제거
      4) 복합 PK(user_id, performance_id) 재생성
    """
    # 1) 유니크 인덱스 제거
    op.execute("DROP INDEX `unique_user_performance` ON `stamp`;")

    # 2) 현재 PK(id) 제거
    op.execute("ALTER TABLE `stamp` DROP PRIMARY KEY;")

    # 3) id 컬럼 제거
    op.drop_column("stamp", "id")

    # 4) 복합 PK 되살리기
    op.execute(
        """
        ALTER TABLE `stamp`
        ADD PRIMARY KEY (`user_id`, `performance_id`);
        """
    )
