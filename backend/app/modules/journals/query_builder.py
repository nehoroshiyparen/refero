from app.infrastructure.database import BaseQueryBuilder
from .models import Journal

class JournalQueryBuilder(BaseQueryBuilder[Journal]):
    def __init__(self, model):
        super().__init__(model)