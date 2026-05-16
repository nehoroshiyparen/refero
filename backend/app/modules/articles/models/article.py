from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer, Boolean, DateTime, func, text
from datetime import datetime

from app.infrastructure.database import BaseModel

if TYPE_CHECKING:
    from app.modules.journals.models.journal import Journal
    from app.modules.articles.models.article_authors import ArticleAuthors
    from app.modules.citations.models.citation import Citation
    from app.modules.users.models.user import User
    from .article_version import ArticleVersion

class Article(BaseModel):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("article_versions.id"), nullable=True
    )

    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    journal_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("journals.id"), nullable=True)
    doi: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    view_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)

    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    creator: Mapped["User"] = relationship(
        back_populates="created_articles",
        foreign_keys=[creator_id],
    )
    journal: Mapped["Journal | None"] = relationship(
        back_populates="articles",
        foreign_keys=[journal_id],
    )
    versions: Mapped[list["ArticleVersion"]] = relationship(
        back_populates="article", cascade="all, delete-orphan",
        order_by="ArticleVersion.version_number",
        foreign_keys="ArticleVersion.article_id",
    )
    current_version: Mapped["ArticleVersion | None"] = relationship(
        primaryjoin="Article.current_version_id == ArticleVersion.id",
        foreign_keys=[current_version_id],
        viewonly=True,
    )
    authors: Mapped[list["ArticleAuthors"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    citations_from: Mapped[list["Citation"]] = relationship(
        foreign_keys="Citation.from_article_id", back_populates="from_article"
    )
    citations_to: Mapped[list["Citation"]] = relationship(
        foreign_keys="Citation.to_article_id", back_populates="to_article"
    )
