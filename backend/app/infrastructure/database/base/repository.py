from typing import TypeVar, Generic, Type
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import Base
from .schemas import ListOptions, SearchOptions

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self._model = model
        self._session = session
    
    async def get_by_id(self, id: int) -> ModelType | None:
        stmt = select(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_list(self, options: ListOptions) -> list[ModelType]:
        stmt = select(self._model).limit(options.limit).offset(options.offset)
        result = await self._session.execute(stmt)
        return result.scalars().all()
    
    async def search_by_filters(self, options: SearchOptions) -> list[ModelType]:
        stmt = (
            select(self._model)
            .limit(options.limit)
            .offset(options.offset)
            .where(*options.filters)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, data: dict) -> ModelType:
        stmt = insert(self._model).values(**data).returning(self._model)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update(self, id: int, data: dict) -> ModelType:
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
    
    def _to_dict(self, entity):
        data = {}
        for c in self.model.__table__.columns:
            data[c.name] = getattr(entity, c.name, None)
        return data