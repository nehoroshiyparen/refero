from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database import Base
from .enum import RoleName

if TYPE_CHECKING:
    from .user import User

class Role(Base):
    __tablename__ = "roles"

    name: Mapped[RoleName] = mapped_column(Enum(RoleName), primary_key=True)

    users: Mapped[list["User"]] = relationship(back_populates="role")