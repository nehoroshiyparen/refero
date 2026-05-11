from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base

class ArticleStatus(Base):
    __tablename__ = "article_statuses"

    name: Mapped[str] = mapped_column(String(20), primary_key=True)