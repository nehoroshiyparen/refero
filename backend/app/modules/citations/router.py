import uuid
from fastapi import APIRouter, Depends

from app.core.responses import SuccessResponse
from app.core.dependencies import require_role
from app.core.deps import get_service

from app.modules.users.models import RoleName
from app.modules.auth.schemas import AccessTokenPayload

from .service import CitationService

router = APIRouter()


@router.get(
    "/{id}/citation-count",
    response_model=SuccessResponse,
    summary="Количество цитирований статьи",
)
async def citation_count(
    id: uuid.UUID,
    service: CitationService = Depends(get_service(CitationService)),
):
    total = await service.count_citations(id)
    return SuccessResponse(data={"total": total})


@router.delete(
    "/{id}",
    response_model=SuccessResponse,
    summary="Удалить цитирование (только автор)",
)
async def delete_citation(
    id: uuid.UUID,
    user: AccessTokenPayload = Depends(require_role([RoleName.AUTHOR])),
    service: CitationService = Depends(get_service(CitationService)),
):
    await service.delete_citation(id, user_id=user.id)
    return SuccessResponse(message="Citation deleted")
