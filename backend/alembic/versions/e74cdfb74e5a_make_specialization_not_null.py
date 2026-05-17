"""make specialization not null

Revision ID: e74cdfb74e5a
Revises: c28f2437cb03
Create Date: 2026-05-17 10:14:27.438642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e74cdfb74e5a'
down_revision: Union[str, Sequence[str], None] = 'c28f2437cb03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE reviewer_profiles SET specialization = 'General' WHERE specialization IS NULL"
    )
    op.alter_column('reviewer_profiles', 'specialization',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)


def downgrade() -> None:
    op.alter_column('reviewer_profiles', 'specialization',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
