from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.infrastructure.database import Base

if TYPE_CHECKING:
    from app.modules.articles.models.arcticle import Article
    from app.modules.users.models.user import User

class ArticleAuthors(Base):
    __tablename__ = "article_authors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    article_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"))
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    article: Mapped["Article"] = relationship(back_populates="authors")
    author: Mapped["User"] = relationship(back_populates="articles_as_author")