"""change_telegram_id_to_bigint

Revision ID: cf3b0e6119ec
Revises: 001
Create Date: 2025-12-18 13:53:33.321663

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf3b0e6119ec'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
