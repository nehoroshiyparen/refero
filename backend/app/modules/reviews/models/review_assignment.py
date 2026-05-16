import uuid
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

from app.infrastructure.database import BaseModel

if TYPE_CHECKING:
    from app.modules.articles.models.article_version import ArticleVersion
    from app.modules.users.models.user import User
    from .review import Review


class ReviewAssignment(BaseModel):
    __tablename__ = "review_assignments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    article_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("article_versions.id", ondelete="CASCADE"), unique=True
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    article_version: Mapped["ArticleVersion"] = relationship(back_populates="review_assignment")
    reviewer: Mapped["User"] = relationship(back_populates="review_assignments")
    review: Mapped["Review | None"] = relationship(
        back_populates="assignment", uselist=False, cascade="all, delete-orphan"
    )
