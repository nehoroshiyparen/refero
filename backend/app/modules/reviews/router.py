import uuid
from fastapi import APIRouter, Depends, status

from app.core.responses import SuccessResponse
from app.core.dependencies import require_role
from app.core.deps import get_service

from app.modules.auth.schemas import AccessTokenPayload
from app.modules.users.models import RoleName

from .service import ReviewService
from .schemas import CreateReviewDTO, UpdateReviewDTO, ReviewFiltersDTO, ReviewPayload

router = APIRouter()
article_reviews_router = APIRouter(prefix="/articles")


@router.get(
    "/",
    response_model=SuccessResponse[list[ReviewPayload]],
    summary="Мои рецензии",
)
async def my_reviews(
    filters: ReviewFiltersDTO = Depends(),
    service: ReviewService = Depends(get_service(ReviewService)),
    user: AccessTokenPayload = Depends(require_role([RoleName.REVIEWER])),
):
    items, meta = await service.get_my_reviews(user_id=user.id, filters=filters)
    return SuccessResponse(
        data=[item.model_dump() for item in items],
        meta=meta
    )


@article_reviews_router.get(
    "/{id}/reviews",
    response_model=SuccessResponse[list[ReviewPayload]],
    summary="Рецензии статьи",
)
async def get_article_reviews(
    id: uuid.UUID,
    service: ReviewService = Depends(get_service(ReviewService)),
    user: AccessTokenPayload = Depends(require_role([RoleName.REVIEWER, RoleName.AUTHOR])),
):
    items = await service.get_article_reviews(article_id=id)
    return SuccessResponse(data=[item.model_dump() for item in items])


@router.post(
    "/",
    response_model=SuccessResponse[ReviewPayload],
    status_code=status.HTTP_201_CREATED,
    summary="Создать рецензию",
)
async def create_review(
    dto: CreateReviewDTO,
    service: ReviewService = Depends(get_service(ReviewService)),
    user: AccessTokenPayload = Depends(require_role([RoleName.REVIEWER])),
):
    result = await service.create_review(dto, user_id=user.id)
    return SuccessResponse(
        message="Review created",
        data=result.model_dump(),
    )


@router.put(
    "/{id}",
    response_model=SuccessResponse[ReviewPayload],
    summary="Обновить рецензию",
)
async def update_review(
    id: uuid.UUID,
    dto: UpdateReviewDTO,
    service: ReviewService = Depends(get_service(ReviewService)),
    user: AccessTokenPayload = Depends(require_role([RoleName.REVIEWER])),
):
    result = await service.update_review(id, dto, user_id=user.id)
    return SuccessResponse(
        message="Review updated",
        data=result.model_dump(),
    )


@router.post(
    "/{id}/revoke",
    response_model=SuccessResponse[ReviewPayload],
    summary="Отозвать рецензию",
)
async def revoke_review(
    id: uuid.UUID,
    service: ReviewService = Depends(get_service(ReviewService)),
    user: AccessTokenPayload = Depends(require_role([RoleName.REVIEWER])),
):
    result = await service.revoke_review(id, user_id=user.id)
    return SuccessResponse(
        message="Review revoked",
        data=result.model_dump(),
    )
