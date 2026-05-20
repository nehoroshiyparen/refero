"""multi role model

Revision ID: cad2ac4b0e9c
Revises: e74cdfb74e5a
Create Date: 2026-05-17 10:41:18.119642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cad2ac4b0e9c'
down_revision: Union[str, Sequence[str], None] = 'e74cdfb74e5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role_name rolename NOT NULL REFERENCES roles(name),
            PRIMARY KEY (user_id, role_name)
        )
    """)
    op.execute(
        "INSERT INTO user_roles (user_id, role_name) SELECT id, role_name FROM users"
    )
    op.execute("ALTER TABLE users DROP CONSTRAINT users_role_name_fkey")
    op.execute("ALTER TABLE users DROP COLUMN role_name")


def downgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN role_name rolename")
    op.execute(
        "UPDATE users SET role_name = ur.role_name::rolename "
        "FROM user_roles ur WHERE users.id = ur.user_id"
    )
    op.execute("UPDATE users SET role_name = 'GUEST' WHERE role_name IS NULL")
    op.execute("ALTER TABLE users ALTER COLUMN role_name SET NOT NULL")
    op.execute(
        "ALTER TABLE users ADD CONSTRAINT users_role_name_fkey "
        "FOREIGN KEY (role_name) REFERENCES roles(name)"
    )
    op.execute("DROP TABLE user_roles")