"""drop magazine_image table

Revision ID: a6f0a9484740
Revises: 64824741caea
Create Date: 2025-09-15 23:10:20.558097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6f0a9484740'
down_revision: Union[str, None] = '64824741caea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade():
    op.execute("DROP TABLE IF EXISTS magazine_image")

def downgrade():
    # 복원이 필요 없다면 비워둬도 됨
    pass
