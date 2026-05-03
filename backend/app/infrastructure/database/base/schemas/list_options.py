from dataclasses import dataclass

@dataclass
class ListOptions:
    limit: int = 20
    offset: int = 0