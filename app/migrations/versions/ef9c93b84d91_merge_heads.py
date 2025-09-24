"""merge heads

Revision ID: ef9c93b84d91
Revises: 8bd4603eb81e, 591c6c0ff59a
Create Date: 2025-09-24 19:35:22.060533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef9c93b84d91'
down_revision: Union[str, None] = ('8bd4603eb81e', '591c6c0ff59a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
