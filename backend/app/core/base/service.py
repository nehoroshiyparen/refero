from abc import ABC
from sqlalchemy.ext.asyncio import AsyncSession

class BaseService(ABC):
    def __init__(self, session: AsyncSession):
        self._session = session