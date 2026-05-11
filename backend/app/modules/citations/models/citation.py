import uuid
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

from app.infrastructure.database import Base

if TYPE_CHECKING:
    from app.modules.articles.models.arcticle import Article

class Citation(Base):
    __tablename__ = "citations"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    from_article_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"))
    to_article_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    from_article: Mapped["Article"] = relationship(foreign_keys=[from_article_id], back_populates="citations_from")
    to_article: Mapped["Article"] = relationship(foreign_keys=[to_article_id], back_populates="citations_to")