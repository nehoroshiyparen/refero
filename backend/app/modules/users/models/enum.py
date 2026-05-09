from enum import Enum

class RoleName(str, Enum):
    GUEST = "GUEST"
    AUTHOR = "AUTHOR"
    REVIEWER = "REVIEWER"
    ADMIN = "ADMIN"