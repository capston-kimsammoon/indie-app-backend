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
      1) add id as NULL
      2) backfill ids
      3) drop existing composite PK (user_id, performance_id)
      4) make id AUTO_INCREMENT + PRIMARY KEY
      5) add UNIQUE(user_id, performance_id)
    """

    # 1) id 컬럼을 우선 NULL 허용으로 추가
    op.add_column("stamp", sa.Column("id", sa.Integer(), nullable=True))

    # 2) 기존 행들에 순번 채워넣기 (MySQL)
    op.execute("SET @i := 0;")
    op.execute(
        """
        UPDATE `stamp`
        SET `id` = (@i := @i + 1)
        ORDER BY `user_id`, `performance_id`, `created_at`;
        """
    )

    # 3) 기존 복합 PK 드롭
    #    이름이 없더라도 MySQL은 PRIMARY KEY 라는 예약명으로 드롭
    op.execute("ALTER TABLE `stamp` DROP PRIMARY KEY;")

    # 4) id를 NOT NULL + AUTO_INCREMENT + PK 로 확정
    op.execute(
        """
        ALTER TABLE `stamp`
        MODIFY COLUMN `id` INT NOT NULL AUTO_INCREMENT,
        ADD PRIMARY KEY (`id`);
        """
    )

    # 5) user_id + performance_id 유니크 제약 추가
    op.execute(
        """
        CREATE UNIQUE INDEX `unique_user_performance`
        ON `stamp`(`user_id`, `performance_id`);
        """
    )


def downgrade() -> None:
    """
    Reverse:
      1) drop UNIQUE(user_id, performance_id)
      2) drop PK(id)
      3) drop id
      4) re-create composite PK(user_id, performance_id)
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
