from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database import Base

if TYPE_CHECKING:
    from .user import User

class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_name: Mapped[str] = mapped_column(ForeignKey("roles.name"), primary_key=True)

    user: Mapped["User"] = relationship(back_populates="user_roles")
