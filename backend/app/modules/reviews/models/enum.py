from enum import Enum

class ReviewStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REQUESTING_CHANGES = "REQUESTING_CHANGES"