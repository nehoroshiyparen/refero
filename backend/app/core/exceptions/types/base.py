from dataclasses import dataclass
from typing import Any

class AppException(Exception):
    message: str
    status_code: int = 400
    code: str = "APP_ERROR"
    details: Any | None = None