"""stub: keep chain consistent; do nothing"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# --- revision identifiers ---
revision: str = "674e14e1d604"
down_revision: Union[str, None] = "27aab79ed338"  # ← 실제로 존재하는 부모만!
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # no-op
    pass

def downgrade() -> None:
    # no-op
    pass
