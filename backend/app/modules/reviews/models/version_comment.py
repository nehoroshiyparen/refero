import uuid
from sqlalchemy import Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

from app.infrastructure.database import BaseModel

if TYPE_CHECKING:
    from app.modules.articles.models.article_version import ArticleVersion
    from app.modules.users.models.user import User


class VersionComment(BaseModel):
    __tablename__ = "version_comments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    article_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("article_versions.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    article_version: Mapped["ArticleVersion"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship()
