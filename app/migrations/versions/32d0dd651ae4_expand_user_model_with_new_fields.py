"""expand user model with new fields"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32d0dd651ae4'
down_revision: Union[str, None] = 'f6d73e2fba61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 새로 추가된 컬럼들
    op.add_column('user', sa.Column('login_id', sa.String(length=12), nullable=True))
    op.add_column('user', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('password_hash', sa.String(length=255), nullable=True))  # ✅ 수정됨
    op.add_column('user', sa.Column('apple_sub', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('apple_email', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('refresh_token', sa.String(length=512), nullable=True))
    op.add_column('user', sa.Column('email_verified', sa.Boolean(), server_default=sa.text("0"), nullable=False))
    op.add_column('user', sa.Column('is_completed', sa.Boolean(), server_default=sa.text("0"), nullable=False))
    op.add_column('user', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False))


def downgrade() -> None:
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_at')
    op.drop_column('user', 'last_login_at')
    op.drop_column('user', 'is_completed')
    op.drop_column('user', 'email_verified')
    op.drop_column('user', 'refresh_token')
    op.drop_column('user', 'apple_email')
    op.drop_column('user', 'apple_sub')
    op.drop_column('user', 'password_hash')
    op.drop_column('user', 'email')
    op.drop_column('user', 'login_id')
