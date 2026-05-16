import uuid
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

from app.infrastructure.database import BaseModel
from .enum import ApprovalStatus

if TYPE_CHECKING:
    from .article_version import ArticleVersion
    from app.modules.users.models.user import User

class ArticleApprovals(BaseModel):
    __tablename__ = "article_approvals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    article_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("article_versions.id", ondelete="CASCADE"))
    approver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    status: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("approval_statuses.name"),
        default=ApprovalStatus.PENDING.value,
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    article_version: Mapped["ArticleVersion"] = relationship(back_populates="approvals")
    approver: Mapped["User"] = relationship(back_populates="approvals_given")
