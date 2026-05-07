from typing import Generic, TypeVar, Type
from sqlalchemy import Select

ModelType = TypeVar("ModelType")

class BaseQueryBuider(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], stmt: Select):
        self._stmt: Select = stmt
        self._model: Type[ModelType] = model
    
    def build(self) -> Select:
        return self._stmt