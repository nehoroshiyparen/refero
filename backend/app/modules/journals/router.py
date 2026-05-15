import uuid
from fastapi import APIRouter, Depends, status

from app.core.responses import SuccessResponse
from app.core.dependencies import require_role, get_current_user
from app.core.deps import get_service

from app.modules.auth.schemas import AccessTokenPayload
from app.modules.users.models import RoleName

from .service import JournalService
from .schemas import CreateJournalDTO, UpdateJournalDTO, JournalPayload

router = APIRouter()


@router.get(
    "/",
    response_model=SuccessResponse[list[JournalPayload]],
    summary="Список журналов",
)
async def get_journals(
    service: JournalService = Depends(get_service(JournalService)),
):
    items = await service.get_journals()
    return SuccessResponse(data=[item.model_dump() for item in items])


@router.get(
    "/{id}",
    response_model=SuccessResponse[JournalPayload],
    summary="Информация о журнале",
)
async def get_journal(
    id: uuid.UUID,
    service: JournalService = Depends(get_service(JournalService)),
):
    result = await service.get_journal(id)
    return SuccessResponse(data=result.model_dump())


@router.post(
    "/",
    response_model=SuccessResponse[JournalPayload],
    status_code=status.HTTP_201_CREATED,
    summary="Создать журнал (admin only)",
)
async def create_journal(
    dto: CreateJournalDTO,
    service: JournalService = Depends(get_service(JournalService)),
    user: AccessTokenPayload = Depends(require_role([RoleName.ADMIN])),
):
    result = await service.create_journal(dto)
    return SuccessResponse(
        message="Journal created",
        data=result.model_dump(),
    )


@router.put(
    "/{id}",
    response_model=SuccessResponse[JournalPayload],
    summary="Обновить журнал (admin only)",
)
async def update_journal(
    id: uuid.UUID,
    dto: UpdateJournalDTO,
    service: JournalService = Depends(get_service(JournalService)),
    user: AccessTokenPayload = Depends(require_role([RoleName.ADMIN])),
):
    result = await service.update_journal(id, dto)
    return SuccessResponse(
        message="Journal updated",
        data=result.model_dump(),
    )


@router.delete(
    "/{id}",
    response_model=SuccessResponse,
    summary="Удалить журнал (admin only)",
)
async def delete_journal(
    id: uuid.UUID,
    service: JournalService = Depends(get_service(JournalService)),
    user: AccessTokenPayload = Depends(require_role([RoleName.ADMIN])),
):
    await service.delete_journal(id)
    return SuccessResponse(message="Journal deleted")
