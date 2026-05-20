from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, TypeVar, Type, Self
from sqlalchemy import Select, select, and_, or_, func

ModelType = TypeVar("ModelType")

class BaseQueryBuilder(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model
        self._stmt: Select = select(model)

    def where(self, *filters, or_: bool = False) -> Self:
        if filters:
            condition = (
                or_(*filters)
                if or_
                else and_(*filters)
            )
            self._stmt = self._stmt.where(condition)
        return self

    def limit(self, limit: int) -> Self:
        self._stmt = self._stmt.limit(limit)
        return self

    def offset(self, offset: int) -> Self:
        self._stmt = self._stmt.offset(offset)
        return self

    def build(self) -> Select:
        return self._stmt

    async def count(self, session: AsyncSession) -> int:
        """Посчитать кол-во записей с учётом фильтров, без limit/offset."""
        # Сбрасываем limit/offset для count-запроса
        subq = self._stmt.subquery()
        count_stmt = select(func.count()).select_from(subq)
        result = await session.execute(count_stmt)
        return result.scalar_one()

    async def all(self, session: AsyncSession) -> list[ModelType]:
        result = await session.execute(self._stmt)
        return list(result.scalars().all())

    async def one_or_none(self, session: AsyncSession) -> ModelType | None:
        result = await session.execute(self._stmt)
        return result.scalar_one_or_none()

    async def first(self, session: AsyncSession) -> ModelType | None:
        result = await session.execute(self._stmt.limit(1))
        return result.scalar_one_or_none()