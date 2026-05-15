from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from .enum import ArticleStatus as ArticleStatusEnum

class ArticleStatusRow(Base):           # ← переименуй чтобы не конфликтовать с enum
    __tablename__ = "article_statuses"
    name: Mapped[str] = mapped_column(String(20), primary_key=True)   # ← просто String