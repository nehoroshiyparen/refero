from .engine import create_db_engine
from app.core.config import settings

engine = create_db_engine(settings.DATABASE_URL)