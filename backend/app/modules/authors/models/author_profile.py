from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database import Base

if TYPE_CHECKING:
    from app.modules.users.models import User

class AuthorProfile(Base):
    __tablename__ = "author_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, )
    
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True, )
    position: Mapped[str | None] = mapped_column(String(255), nullable=True, )

    degree: Mapped[str | None] = mapped_column(String(100), nullable=True, )
    orcid: Mapped[str | None] = mapped_column(String(50), nullable=True, )

    bio: Mapped[str| None] = mapped_column(Text, nullable=True, )

    user: Mapped["User"] = relationship(back_populates="author_profile")