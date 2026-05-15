from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from .enum import ApprovalStatus as ApprovalStatusEnum

class ApprovalStatusRow(Base):
    __tablename__ = "approval_statuses"
    name: Mapped[str] = mapped_column(String(20), primary_key=True)