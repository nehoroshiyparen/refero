from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum as PyEnum

import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ARRAY, VARCHAR, DateTime, ForeignKey, Integer, func, Enum
from datetime import datetime

from app.infrastructure.database import Base
from .enum import ArticleStatus

if TYPE_CHECKING:
    from app.modules.journals.models.journal import Journal
    from app.modules.articles.models.article_authors import ArticleAuthors
    from app.modules.articles.models.article_approvals import ArticleApprovals
    from app.modules.citations.models.citation import Citation
    from app.modules.reviews.models import Review
    from app.modules.users.models.user import User

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    title: Mapped[str] = mapped_column(String, nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=True)
    keywords: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    language: Mapped[str] = mapped_column(VARCHAR(5), default="en")

    doi: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    pdf_path: Mapped[str] = mapped_column(String, nullable=False)
    
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    journal_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("journals.id"), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("article_statuses.name"),
        default=ArticleStatus.DRAFT.value,
    )

    view_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    journal: Mapped["Journal | None"] = relationship(back_populates="articles")
    authors: Mapped[list["ArticleAuthors"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    creator: Mapped["User"] = relationship(back_populates="created_articles", foreign_keys=[creator_id])
    approvals: Mapped[list["ArticleApprovals"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    citations_from: Mapped[list["Citation"]] = relationship(foreign_keys="Citation.from_article_id", back_populates="from_article")
    citations_to: Mapped[list["Citation"]] = relationship(foreign_keys="Citation.to_article_id", back_populates="to_article")
    updated_by_user: Mapped["User | None"] = relationship(foreign_keys=[updated_by_user_id])