from pydantic import BaseModel

class ApprovalSubmissionPayload(BaseModel):
    """Ответ после submit-for-approval."""
    message: str