"""default role to author

Revision ID: 25002c04d734
Revises: e74cdfb74e5a
Create Date: 2026-05-17 10:24:43.232256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25002c04d734'
down_revision: Union[str, Sequence[str], None] = 'e74cdfb74e5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE users SET role_name = 'AUTHOR' WHERE role_name = 'GUEST'"
    )


def downgrade() -> None:
    pass
