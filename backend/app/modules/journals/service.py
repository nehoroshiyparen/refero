import uuid

from app.core.base import BaseService
from app.core.exceptions import NotFound, BadRequest

from .repository import JournalRepository
from .models import Journal
from .schemas import CreateJournalDTO, UpdateJournalDTO, JournalPayload


class JournalService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self._journal_repo = JournalRepository(self._session)

    async def get_journals(self) -> list[JournalPayload]:
        items = await self._journal_repo.query().all(self._session)
        return [self._to_payload(j) for j in items]

    async def get_journal(self, id: uuid.UUID) -> JournalPayload:
        journal = await self._get_or_fail(id)
        return self._to_payload(journal)

    async def create_journal(self, dto: CreateJournalDTO) -> JournalPayload:
        journal = await self._journal_repo.create({
            "id": str(uuid.uuid4()),
            "name": dto.name,
            "issn": dto.issn,
            "description": dto.description,
        })
        return self._to_payload(journal)

    async def update_journal(self, id: uuid.UUID, dto: UpdateJournalDTO) -> JournalPayload:
        await self._get_or_fail(id)

        data = dto.model_dump(exclude_unset=True)
        if not data:
            raise BadRequest("No fields to update")

        updated = await self._journal_repo.update(id, data)
        return self._to_payload(updated)

    async def delete_journal(self, id: uuid.UUID) -> None:
        await self._get_or_fail(id)
        await self._journal_repo.delete(id)

    # ------------------------------------------------------------------ #
    #  HELPERS
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_payload(journal: Journal) -> JournalPayload:
        return JournalPayload(
            id=journal.id,
            name=journal.name,
            issn=journal.issn,
            description=journal.description,
            created_at=journal.created_at,
        )

    async def _get_or_fail(self, id: uuid.UUID) -> Journal:
        journal = await (
            self._journal_repo.query()
            .where(Journal.id == id)
            .one_or_none(self._session)
        )
        if not journal:
            raise NotFound("Journal not found")
        return journal
