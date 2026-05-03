from dataclasses import dataclass, field
from sqlalchemy import ColumnElement
from .list_options import ListOptions

@dataclass
class SearchOptions(ListOptions):
    filters: list[ColumnElement] = field(default_factory=list)