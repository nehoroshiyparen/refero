from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base

class ReviewStatus(Base):
    __tablename__ = "review_statuses"

    name: Mapped[str] = mapped_column(String(20), primary_key=True)