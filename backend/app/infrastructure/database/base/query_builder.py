from typing import Generic, TypeVar, Type, Self
from sqlalchemy import Select, select, and_, or_

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