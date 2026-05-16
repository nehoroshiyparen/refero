"""

Revision ID: afa4c8f8e1c1
Revises: c8d6eb10e6b5
Create Date: 2026-05-16 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'afa4c8f8e1c1'
down_revision: Union[str, Sequence[str], None] = 'c8d6eb10e6b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('articles', 'is_visible',
                    existing_type=sa.Boolean(),
                    server_default=sa.text('true'),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('articles', 'is_visible',
                    existing_type=sa.Boolean(),
                    server_default=None,
                    existing_nullable=False)
