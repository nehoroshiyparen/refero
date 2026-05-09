from uuid import UUID

from app.core.base import BaseService

from .repository import AuthorRepository, AuthorProfile

class AuthorService(BaseService):
    def __init__(self):
        self._author_repo = AuthorRepository()

    async def create_profile(self, data: any):
        pass