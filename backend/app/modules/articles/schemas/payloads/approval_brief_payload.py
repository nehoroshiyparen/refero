import uuid
from datetime import datetime
from pydantic import BaseModel

from ...models.enum import ApprovalStatus


class ApprovalBriefPayload(BaseModel):
    id: uuid.UUID
    approver_id: uuid.UUID
    approver_name: str
    status: ApprovalStatus
    comment: str | None = None
    approved_at: datetime | None = None
