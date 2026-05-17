from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database import Base

if TYPE_CHECKING:
    from .user import User

class ReviewerProfile(Base):
    __tablename__ = "reviewer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    specialization: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[str | None] = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="reviewer_profile")
