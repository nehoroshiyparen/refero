from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from sqlalchemy import Integer, String, Boolean, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.infrastructure.database import Base
from .enum import RoleName

if TYPE_CHECKING:
    from .role import Role
    from app.modules.authors.models.author_profile import AuthorProfile
    from app.modules.reviewers.models.reviewer_profile import ReviewerProfile
    from app.modules.auth.models import RefreshToken

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, )

    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, )
    
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, )

    full_name: Mapped[str] = mapped_column(String(255), nullable=False, )
    
    avatar_url: Mapped[str | None] = mapped_column(String(500))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role_name: Mapped[RoleName] = mapped_column(Enum(RoleName), ForeignKey("roles.name"), nullable=False, default=RoleName.GUEST)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    role: Mapped["Role"] = relationship(back_populates="users")

    author_profile: Mapped["AuthorProfile | None"] = relationship(
        back_populates="user", uselist=False
    )
    reviewer_profile: Mapped["ReviewerProfile | None"] = relationship(
        back_populates="user", uselist=False
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )