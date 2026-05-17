"""make orcid not null

Revision ID: 02fd27897f92
Revises: afa4c8f8e1c1
Create Date: 2026-05-17 10:09:26.006413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02fd27897f92'
down_revision: Union[str, Sequence[str], None] = 'afa4c8f8e1c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE author_profiles SET orcid = '0000-0000-0000-0000' WHERE orcid IS NULL"
    )
    op.alter_column('author_profiles', 'orcid',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)


def downgrade() -> None:
    op.alter_column('author_profiles', 'orcid',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
