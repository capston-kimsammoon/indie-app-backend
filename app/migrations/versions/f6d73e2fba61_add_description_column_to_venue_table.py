"""add description column to venue table

Revision ID: f6d73e2fba61
Revises: 76f7b3aee2c1
Create Date: 2025-10-13 14:03:20.823673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6d73e2fba61'
down_revision: Union[str, None] = '76f7b3aee2c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('venue', sa.Column('description', sa.String(length=200), nullable=True))

def downgrade() -> None:
    op.drop_column('venue', 'description')
