"""make orcid unique

Revision ID: c28f2437cb03
Revises: 02fd27897f92
Create Date: 2026-05-17 10:11:13.803948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c28f2437cb03'
down_revision: Union[str, Sequence[str], None] = '02fd27897f92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE author_profiles SET orcid = '0000-0001-2345-6789' "
        "WHERE orcid = '0000-0000-0000-0000'"
    )
    op.create_unique_constraint('author_profiles_orcid_key', 'author_profiles', ['orcid'])


def downgrade() -> None:
    op.drop_constraint('author_profiles_orcid_key', 'author_profiles', type_='unique')
