"""merge multiple heads

Revision ID: f3415a3ab6c7
Revises: 27aab79ed338, 674e14e1d604
Create Date: 2025-09-24 18:58:20.989815

"""
"""merge multiple heads (linearized)"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "f3415a3ab6c7"
down_revision: Union[str, None] = "674e14e1d604"  # 단일 부모로 정리
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
