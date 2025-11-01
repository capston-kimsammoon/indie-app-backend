"""create music_magazine tables

Revision ID: 71ac506526e4
Revises: 32d0dd651ae4
Create Date: 2025-10-29 21:50:58.836586

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71ac506526e4'
down_revision: Union[str, None] = '32d0dd651ae4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1) music_magazine 테이블
    op.create_table(
        "music_magazine",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_music_magazine_id",
        "music_magazine",
        ["id"],
        unique=False
    )

    # 2) Enum 정의 (블록 타입: text | image | divider | cta)
    music_mag_block_type = sa.Enum(
        "text",
        "image",
        "divider",
        "cta",
        name="music_mag_block_type"
    )

    # 3) music_magazine_block 테이블
    op.create_table(
        "music_magazine_block",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "magazine_id",
            sa.Integer(),
            sa.ForeignKey("music_magazine.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "display_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0")
        ),
        sa.Column("type", music_mag_block_type, nullable=False),
        sa.Column("semititle", sa.String(length=200), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column(
            "artist_id",
            sa.Integer(),
            sa.ForeignKey("artist.id"),
            nullable=True,
        ),
    )

    # 4) 인덱스들
    op.create_index(
        "ix_music_mag_block_magazine_id",
        "music_magazine_block",
        ["magazine_id"],
        unique=False
    )
    op.create_index(
        "ix_music_mag_block_order",
        "music_magazine_block",
        ["display_order"],
        unique=False
    )
    op.create_index(
        "ix_music_mag_block_artist_id",
        "music_magazine_block",
        ["artist_id"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    # 생성 역순으로 드랍
    op.drop_index("ix_music_mag_block_artist_id", table_name="music_magazine_block")
    op.drop_index("ix_music_mag_block_order", table_name="music_magazine_block")
    op.drop_index("ix_music_mag_block_magazine_id", table_name="music_magazine_block")
    op.drop_table("music_magazine_block")

    op.drop_index("ix_music_magazine_id", table_name="music_magazine")
    op.drop_table("music_magazine")

    # PostgreSQL을 사용하는 경우 Enum 타입을 명시적으로 삭제해야 할 수 있음
    # (MySQL은 테이블 드랍 시 Enum 타입이 같이 정리됨)
    try:
        sa.Enum(name="music_mag_block_type").drop(op.get_bind(), checkfirst=True)
    except Exception:
        # DB 백엔드/상황에 따라 이미 정리되었을 수 있음
        pass
