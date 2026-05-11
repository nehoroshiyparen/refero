from app.core.base import BaseService

from .repositories import (
    ArticleRepository,
    ArticleAuthorsRepository,
    ArticleApprovalsRepository,
)
from .schemas import (
    ArticleCreateDTO,
    ArticleUpdateDTO
)

class ArticleService(BaseService):
    def __init__(self, session):
        super().__init__(session)

        self._article_repo = ArticleRepository(self._session)
        self._article_approvals_repo = ArticleApprovalsRepository(self._session)
        self._article_authors_repo = ArticleAuthorsRepository(self._session)

    async def get_articles(self):
        pass

    async def get_article_by_id(self, id: int):
        pass

    async def create_article(
        self,
        dto: ArticleCreateDTO,
    ):
        pass

    async def update_article(
        self,
        id: int,
        dto: ArticleUpdateDTO,
    ):
        pass

    async def delete_article(
        self,
        id: int,
    ):
        pass

    async def submit_for_approval(
        self,
        id: int,
    ):
        pass

    async def add_author(
        self,
        id: int,
    ):
        pass

    async def delete_author(
        self,
        id: int,
    ):
        pass

    async def download_article(
        self,
        id: int,
    ):
        pass