from typing import Type
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_session
from .base import BaseService

from .exceptions import (
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,

    AppException
) 

def get_service(service_class: Type[BaseService]):
    def dependency(session: AsyncSession = Depends(get_session)):
        return service_class(session)
    return dependency

def setup_handlers(app: FastAPI):
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)