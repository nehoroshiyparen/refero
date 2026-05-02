import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database import Base
from .user import User

class ReviewerProfile(Base):
    __tablename__ = "reviewer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    specialization: Mapped[str | None] = mapped_column(String(255))
    degree: Mapped[str | None] = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="reviewer_profile")