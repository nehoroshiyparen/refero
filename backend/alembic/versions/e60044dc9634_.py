"""...

Revision ID: e60044dc9634
Revises: fa757eb66006
Create Date: 2026-05-11 20:09:32.426820

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e60044dc9634'
down_revision: Union[str, Sequence[str], None] = 'fa757eb66006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Lookup tables ──────────────────────────────────────────
    op.create_table('article_statuses',
        sa.Column('name', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('name')
    )
    op.create_table('approval_statuses',
        sa.Column('name', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('name')
    )
    op.create_table('review_statuses',
        sa.Column('name', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('name')
    )
    op.create_table('journals',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('issn', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # ── Articles ───────────────────────────────────────────────
    op.create_table('articles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('keywords', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('language', sa.VARCHAR(length=5), nullable=False),
        sa.Column('doi', sa.String(), nullable=True),
        sa.Column('pdf_path', sa.String(), nullable=False),
        sa.Column('journal_id', sa.Uuid(), nullable=True),
        # String + FK вместо sa.Enum()
        sa.Column('status', sa.String(length=20), nullable=False, server_default='DRAFT'),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('download_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_by_user_id', sa.Uuid(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['journal_id'], ['journals.id']),
        sa.ForeignKeyConstraint(['status'], ['article_statuses.name']),
        sa.ForeignKeyConstraint(['updated_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doi')
    )

    # ── Article Approvals ──────────────────────────────────────
    op.create_table('article_approvals',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('article_id', sa.Uuid(), nullable=False),
        sa.Column('approver_id', sa.Uuid(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['status'], ['approval_statuses.name']),
        sa.PrimaryKeyConstraint('id')
    )

    # ── Article Authors ────────────────────────────────────────
    op.create_table('article_authors',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('article_id', sa.Uuid(), nullable=False),
        sa.Column('author_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ── Citations ──────────────────────────────────────────────
    op.create_table('citations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('from_article_id', sa.Uuid(), nullable=False),
        sa.Column('to_article_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['from_article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ── Reviews ────────────────────────────────────────────────
    op.create_table('reviews',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('article_id', sa.Uuid(), nullable=False),
        sa.Column('reviewer_id', sa.Uuid(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['status'], ['review_statuses.name']),
        sa.PrimaryKeyConstraint('id')
    )

    # ── Seed data ──────────────────────────────────────────────
    for s in ["DRAFT", "PENDING_APPROVAL", "REVIEW", "PUBLISHED", "REJECTED"]:
        op.execute(f"INSERT INTO article_statuses (name) VALUES ('{s}') ON CONFLICT (name) DO NOTHING")

    for s in ["PENDING", "APPROVED", "REJECTED"]:
        op.execute(f"INSERT INTO approval_statuses (name) VALUES ('{s}') ON CONFLICT (name) DO NOTHING")

    for s in ["PENDING", "APPROVED", "REJECTED", "REQUESTING_CHANGES"]:
        op.execute(f"INSERT INTO review_statuses (name) VALUES ('{s}') ON CONFLICT (name) DO NOTHING")

    # ── Удалить старые PG enum-ы если существуют ───────────────
    # (от предыдущих миграций)
    op.execute("DROP TYPE IF EXISTS articlestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS approvalstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS reviewstatus CASCADE")


def downgrade() -> None:
    op.drop_table('reviews')
    op.drop_table('citations')
    op.drop_table('article_authors')
    op.drop_table('article_approvals')
    op.drop_table('articles')
    op.drop_table('journals')
    op.drop_table('review_statuses')
    op.drop_table('approval_statuses')
    op.drop_table('article_statuses')