import enum

class CitationMatchStatus(str, enum.Enum):
    LINKED = "linked"        # Обе статьи на платформе, связь установлена
    PENDING = "pending"      # DOI есть, но статьи на платформе нет
    EXTERNAL = "external"    # Просто текст, внешняя ссылка