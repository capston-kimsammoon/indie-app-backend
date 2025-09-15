"""add magazine_block table

Revision ID: 64824741caea
Revises: 25c16e5a0a9b
Create Date: 2025-09-15 22:56:48.163653

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64824741caea'
down_revision: Union[str, None] = '25c16e5a0a9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        "magazine_block",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("magazine_id", sa.Integer(),
                  sa.ForeignKey("magazine.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("type", sa.Enum("text","image","quote","embed","divider", name="mag_block_type"),
                  nullable=False, server_default="text"),
        sa.Column("text", sa.Text()),
        sa.Column("image_url", sa.String(500)),
        sa.Column("caption", sa.String(300)),
        sa.Column("align", sa.Enum("left","center","right", name="mag_img_align"),
                  server_default="center"),
        sa.Column("meta", sa.JSON()),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    # 인덱스(조회 최적화)
    op.create_index("ix_magazine_block_id", "magazine_block", ["id"])
    op.create_index("ix_magazine_block_magazine_id_order", "magazine_block", ["magazine_id", "order"])

def downgrade():
    op.drop_index("ix_magazine_block_magazine_id_order", table_name="magazine_block")
    op.drop_index("ix_magazine_block_id", table_name="magazine_block")
    op.drop_table("magazine_block")

