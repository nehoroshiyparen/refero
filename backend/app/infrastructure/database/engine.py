from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Engine
from app.core.config import settings

def create_db_engine(database_url: str) -> Engine:
    return create_async_engine(
        database_url,
        pool_recycle=60,
        pool_pre_ping=True,
    )