import uuid
from sqlalchemy import Text, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

from app.infrastructure.database import Base
from .enum import ReviewStatus

if TYPE_CHECKING:
    from backend.app.modules.articles.models.article import Article
    from app.modules.users.models.user import User

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    article_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"))
    reviewer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    status: Mapped[str] = mapped_column(String, default=ReviewStatus.PENDING)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    article: Mapped["Article"] = relationship(back_populates="reviews")
    reviewer: Mapped["User"] = relationship(back_populates="reviews_as_reviewer")