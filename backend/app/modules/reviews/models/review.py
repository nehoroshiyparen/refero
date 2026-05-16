import uuid
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

from app.infrastructure.database import BaseModel
from .enum import ReviewStatus

if TYPE_CHECKING:
    from .review_assignment import ReviewAssignment

class Review(BaseModel):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    review_assignment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("review_assignments.id", ondelete="CASCADE"), unique=True
    )

    status: Mapped[str] = mapped_column(String, default=ReviewStatus.APPROVED)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    assignment: Mapped["ReviewAssignment"] = relationship(back_populates="review")
