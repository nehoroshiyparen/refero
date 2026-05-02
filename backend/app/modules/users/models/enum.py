from enum import Enum

class RoleName(str, Enum):
    GUEST = "guest"
    AUTHOR = "author"
    REVIEWER = "reviewer"
    ADMIN = "admin"