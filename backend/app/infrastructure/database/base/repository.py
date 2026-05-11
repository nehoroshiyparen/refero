from typing import TypeVar, Generic, Type
from sqlalchemy import select, insert, update, delete, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import Base
from .query_builder import BaseQueryBuilder
from .schemas import ListOptions, SearchOptions

ModelType = TypeVar("ModelType", bound=Base)
QueryBuilderType = TypeVar("QueryBuilderType", bound=BaseQueryBuilder)

class BaseRepository(Generic[ModelType, QueryBuilderType]):
    _query_builder: type[QueryBuilderType]
    _model: type[ModelType]

    def __init__(self, session: AsyncSession):
        self._session = session

    def query(self) -> QueryBuilderType:
        return self._query_builder(self._model)

    async def create(self, data: dict) -> ModelType:
        stmt = insert(self._model).values(**data).returning(self._model)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update(self, id: int, data: dict) -> ModelType | None:
        filtered = {k: v for k, v in data.items() if v is not None}
        stmt = update(self._model).where(self._model.id == id).values(**filtered).returning(self._model)
        result = await self._session.execute(stmt)
        updated = result.scalar_one_or_none()
        return updated
    
    async def delete(self, id: int) -> bool:
        stmt = delete(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        if result.rowcount == 0:
            return False
        return True
    
    def _build_filter_stmt(self, options: SearchOptions):
        stmt = select(self._model)

        if options.filters:
            condition = (
                or_(*options.filters)
                if options.or_
                else and_(*options.filters)
            )
            stmt = stmt.where(condition)

        return stmt
    
    def _to_dict(self, entity):
        data = {}
        for c in self._model.__table__.columns:
            data[c.name] = getattr(entity, c.name, None)
        return data