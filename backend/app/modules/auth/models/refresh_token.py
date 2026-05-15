from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database import BaseModel
from datetime import datetime

if TYPE_CHECKING:
    from app.modules.users.models import User

class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    token_hash: Mapped[str] = mapped_column(String, nullable=False, )

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")