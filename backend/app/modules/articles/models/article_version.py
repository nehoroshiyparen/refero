from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, ARRAY, VARCHAR, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.infrastructure.database import BaseModel

from .enum import ArticleStatus

if TYPE_CHECKING:
    from .article import Article
    from .article_approvals import ArticleApprovals
    from app.modules.reviews.models.review_assignment import ReviewAssignment
    from app.modules.reviews.models.version_comment import VersionComment
    from app.modules.users.models.user import User

class ArticleVersion(BaseModel):
    __tablename__ = "article_versions"

    __table_args__ = (
        UniqueConstraint("article_id", "version_number", name="uq_article_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str] = mapped_column(String, nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    language: Mapped[str] = mapped_column(VARCHAR(5), default="en")
    pdf_path: Mapped[str] = mapped_column(String, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20), ForeignKey("article_statuses.name"),
        default=ArticleStatus.DRAFT.value,
    )
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    article: Mapped["Article"] = relationship(
        back_populates="versions",
        foreign_keys=[article_id],
    )
    updated_by_user: Mapped["User | None"] = relationship(
        foreign_keys=[updated_by_user_id],
    )
    approvals: Mapped[list["ArticleApprovals"]] = relationship(
        back_populates="article_version", cascade="all, delete-orphan"
    )
    review_assignment: Mapped["ReviewAssignment | None"] = relationship(
        back_populates="article_version", uselist=False, cascade="all, delete-orphan"
    )
    comments: Mapped[list["VersionComment"]] = relationship(
        back_populates="article_version", cascade="all, delete-orphan"
    )
