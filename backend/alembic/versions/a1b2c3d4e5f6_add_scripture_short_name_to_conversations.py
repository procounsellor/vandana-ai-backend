"""add scripture_short_name to conversations

Revision ID: a1b2c3d4e5f6
Revises: d895537ca09d
Create Date: 2026-03-29 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'd895537ca09d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('conversations', sa.Column('scripture_short_name', sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column('conversations', 'scripture_short_name')
