import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse

from app.core.responses import SuccessResponse
from app.core.dependencies import get_current_user, require_role
from app.core.deps import get_service
from app.modules.auth.schemas import AccessTokenPayload
from app.modules.users.models import RoleName

from .service import ArticleService
from .schemas import (
    ArticleUpdateDTO,
    ArticleCreateDTO,
    ArticleFiltersDTO,
    AddAuthorDTO,
)

router = APIRouter()


@router.get(
    "/",
    response_model=SuccessResponse,
    summary="Список статей с фильтрацией",
)
async def get_articles(
    filters: ArticleFiltersDTO = Depends(),
    service: ArticleService = Depends(get_service(ArticleService)),
):
    items, meta = await service.get_articles(filters)
    return SuccessResponse(
        data=[item.model_dump() for item in items],
        meta=meta.model_dump(),
    )


@router.get(
    "/{id}",
    response_model=SuccessResponse,
    summary="Статья по ID",
)
async def get_article_by_id(
    id: uuid.UUID,
    anonymous: bool = False,
    service: ArticleService = Depends(get_service(ArticleService)),
):
    result = await service.get_article_by_id(id, anonymous=anonymous)
    return SuccessResponse(data=result.model_dump())


@router.post(
    "/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать статью",
)
async def create_article(
    dto: ArticleCreateDTO,
    user: AccessTokenPayload = Depends(require_role([RoleName.AUTHOR])),
    service: ArticleService = Depends(get_service(ArticleService)),
):
    result = await service.create_article(dto, user_id=user.id)
    return SuccessResponse(
        message="Article created",
        data=result.model_dump(),
    )


@router.put(
    "/{id}",
    response_model=SuccessResponse,
    summary="Обновить статью",
)
async def update_article(
    id: uuid.UUID,
    dto: ArticleUpdateDTO,
    user: AccessTokenPayload = Depends(require_role([RoleName.AUTHOR])),
    service: ArticleService = Depends(get_service(ArticleService)),
):
    result = await service.update_article(id, dto, user_id=user.id)
    return SuccessResponse(
        message="Article updated",
        data=result.model_dump(),
    )


@router.delete(
    "/{id}",
    response_model=SuccessResponse,
    summary="Удалить статью",
)
async def delete_article(
    id: uuid.UUID,
    user: AccessTokenPayload = Depends(require_role([RoleName.AUTHOR])),
    service: ArticleService = Depends(get_service(ArticleService)),
):
    await service.delete_article(id, user_id=user.id)
    return SuccessResponse(message="Article deleted")


@router.post(
    "/{id}/submit-for-approval",
    response_model=SuccessResponse,
    summary="Отправить на апрув соавторам",
)
async def submit_for_approval(
    id: uuid.UUID,
    user: AccessTokenPayload = Depends(require_role([RoleName.AUTHOR])),
    service: ArticleService = Depends(get_service(ArticleService)),
):
    result = await service.submit_for_approval(id, user_id=user.id)
    return SuccessResponse(
        message=result.message,
        data=result.model_dump(),
    )


@router.post(
    "/{id}/authors",
    response_model=SuccessResponse,
    summary="Добавить соавтора",
)
async def add_author(
    id: uuid.UUID,
    dto: AddAuthorDTO,
    user: AccessTokenPayload = Depends(require_role([RoleName.AUTHOR])),
    service: ArticleService = Depends(get_service(ArticleService)),
):
    result = await service.add_author(id, dto, user_id=user.id)
    return SuccessResponse(
        message=result.message,
        data=result.model_dump(),
    )


@router.delete(
    "/{id}/authors/{author_id}",
    response_model=SuccessResponse,
    summary="Удалить соавтора",
)
async def delete_author(
    id: uuid.UUID,
    author_id: uuid.UUID,
    user: AccessTokenPayload = Depends(require_role([RoleName.AUTHOR])),
    service: ArticleService = Depends(get_service(ArticleService)),
):
    result = await service.delete_author(id, author_id, user_id=user.id)
    return SuccessResponse(
        message=result.message,
        data=result.model_dump(),
    )


@router.get(
    "/{id}/download",
    summary="Скачать PDF статьи",
)
async def download_article(
    id: uuid.UUID,
    service: ArticleService = Depends(get_service(ArticleService)),
):
    pdf_path = await service.download_article(id)
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.split("/")[-1],
    )


@router.post(
    "/{id}/hide",
    response_model=SuccessResponse,
    summary="Скрыть статью",
)
async def hide_article(
    id: uuid.UUID,
    user: AccessTokenPayload = Depends(require_role([RoleName.AUTHOR])),
    service: ArticleService = Depends(get_service(ArticleService)),
):
    result = await service.hide_article(id, user_id=user.id)
    return SuccessResponse(
        message="Article hidden",
        data=result.model_dump(),
    )


@router.post(
    "/{id}/show",
    response_model=SuccessResponse,
    summary="Показать статью",
)
async def show_article(
    id: uuid.UUID,
    user: AccessTokenPayload = Depends(require_role([RoleName.AUTHOR])),
    service: ArticleService = Depends(get_service(ArticleService)),
):
    result = await service.show_article(id, user_id=user.id)
    return SuccessResponse(
        message="Article shown",
        data=result.model_dump(),
    )
