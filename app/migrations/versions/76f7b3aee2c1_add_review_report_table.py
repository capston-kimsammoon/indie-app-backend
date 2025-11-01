"""add review_report table"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '76f7b3aee2c1'      # 그대로 두세요
down_revision: Union[str, None] = 'bc4df0c6e40d'  # 그대로 두세요
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'review_report',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('review_id', sa.Integer, sa.ForeignKey('review.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reason', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('review_report')
