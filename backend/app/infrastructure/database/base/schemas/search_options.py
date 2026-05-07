from dataclasses import dataclass, field
from sqlalchemy import ColumnElement
from .list_options import ListOptions

@dataclass
class SearchOptions(ListOptions):
    filters: list[ColumnElement] = field(default_factory=list)
    or_: bool = False
    and_: bool = False