"""comment cascade fks

Revision ID: b75bc402c646
Revises: 6368804e031e
Create Date: 2025-08-16 18:59:43.495469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b75bc402c646'
down_revision: Union[str, None] = '6368804e031e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint("comment_post_id_fkey", "comment", type_="foreignkey")
    op.create_foreign_key(
        "comment_post_id_fkey",
        "comment", "post",
        ["post_id"], ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("comment_parent_comment_id_fkey", "comment", type_="foreignkey")
    op.create_foreign_key(
        "comment_parent_comment_id_fkey",
        "comment", "comment",
        ["parent_comment_id"], ["id"],
        ondelete="CASCADE",
    )

def downgrade():
    op.drop_constraint("comment_post_id_fkey", "comment", type_="foreignkey")
    op.create_foreign_key(
        "comment_post_id_fkey",
        "comment", "post",
        ["post_id"], ["id"],
        ondelete=None,
    )

    op.drop_constraint("comment_parent_comment_id_fkey", "comment", type_="foreignkey")
    op.create_foreign_key(
        "comment_parent_comment_id_fkey",
        "comment", "comment",
        ["parent_comment_id"], ["id"],
        ondelete=None,
    )