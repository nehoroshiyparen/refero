from dataclasses import dataclass
from typing import Any
from .base import AppException

# =>400 & <500
@dataclass
class BadRequest(AppException):
    message: str = "Bad request"
    status_code: int = 400
    code: str = "BAD_REQUEST"
    details: Any | None = None

@dataclass
class Unauthorized(AppException):
    message: str = "Unauthorized"
    status_code: int = 401
    code: str = "UNAUTHORIZED"
    details: Any | None = None

@dataclass
class Forbidden(AppException):
    message: str = "Forbidden"
    status_code: int = 403
    code: str = "FORBIDDEN"
    details: Any | None = None

@dataclass
class NotFound(AppException):
    message: str = "Not found"
    status_code: int = 404
    code: str = "NOT_FOUND"
    details: Any | None = None

@dataclass
class Conflict(AppException):
    message: str = "Conflict"
    status_code: int = 409
    code: str = "CONFLICT"
    details: Any | None = None

# =>500
@dataclass
class InternalError(AppException):
    message: str = "Internal server error"
    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    details: Any | None = None