from typing import Type

from app.infrastructure.database import BaseQueryBuilder

from .models import Citation

class CitationQueryBuilder(BaseQueryBuilder[Citation]):
    def __init__(self, model):
        super().__init__(model)