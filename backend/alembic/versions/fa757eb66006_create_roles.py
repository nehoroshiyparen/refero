"""create_roles

Revision ID: fa757eb66006
Revises: a8c56a83808f
Create Date: 2026-05-07 18:37:53.854892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa757eb66006'
down_revision: Union[str, Sequence[str], None] = 'a8c56a83808f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        INSERT INTO roles (name) VALUES
        ('GUEST'),
        ('AUTHOR'),
        ('REVIEWER'),
        ('ADMIN')
        ON CONFLICT DO NOTHING;
    """)


def downgrade():
    op.execute("""
        DELETE FROM roles WHERE name IN
        ('GUEST', 'AUTHOR', 'REVIEWER', 'ADMIN')
    """)
