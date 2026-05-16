import uuid
from fastapi import APIRouter, Depends, status

from app.core.responses import SuccessResponse
from app.core.dependencies import require_role
from app.core.deps import get_service

from app.modules.auth.schemas import AccessTokenPayload
from app.modules.users.models import RoleName

from .service import ReviewService
from .schemas import (
    CreateReviewDTO,
    CreateCommentDTO,
    ReviewPayload,
    ReviewAssignmentFullPayload,
    CommentPayload,
)

router = APIRouter()
article_reviews_router = APIRouter(prefix="/articles")


@router.get(
    "/assignments",
    response_model=SuccessResponse[list[ReviewAssignmentFullPayload]],
    summary="Мои назначения на ревью",
)
async def my_assignments(
    service: ReviewService = Depends(get_service(ReviewService)),
    user: AccessTokenPayload = Depends(require_role([RoleName.REVIEWER])),
):
    result = await service.get_my_assignments(user_id=user.id)
    return SuccessResponse(data=[item.model_dump() for item in result])


@router.post(
    "/assignments/{assignment_id}/review",
    response_model=SuccessResponse[ReviewPayload],
    status_code=status.HTTP_201_CREATED,
    summary="Вынести решение по ревью",
)
async def create_review(
    assignment_id: uuid.UUID,
    dto: CreateReviewDTO,
    service: ReviewService = Depends(get_service(ReviewService)),
    user: AccessTokenPayload = Depends(require_role([RoleName.REVIEWER])),
):
    dto_dict = dto.model_dump()
    dto_dict["review_assignment_id"] = assignment_id
    result = await service.create_review(CreateReviewDTO(**dto_dict), user_id=user.id)
    return SuccessResponse(
        message="Review submitted",
        data=result.model_dump(),
    )


@router.get(
    "/assignments/{assignment_id}/review",
    response_model=SuccessResponse[ReviewPayload | None],
    summary="Получить ревью по назначению",
)
async def get_review_by_assignment(
    assignment_id: uuid.UUID,
    service: ReviewService = Depends(get_service(ReviewService)),
):
    result = await service.get_review_by_assignment(assignment_id)
    return SuccessResponse(data=result.model_dump() if result else None)


# ── Comments ───────────────────────────────────────────────────


@router.get(
    "/versions/{version_id}/comments",
    response_model=SuccessResponse[list[CommentPayload]],
    summary="Комментарии к версии",
)
async def get_comments(
    version_id: uuid.UUID,
    service: ReviewService = Depends(get_service(ReviewService)),
):
    result = await service.get_comments(version_id)
    return SuccessResponse(data=[item.model_dump() for item in result])


@router.post(
    "/versions/{version_id}/comments",
    response_model=SuccessResponse[CommentPayload],
    status_code=status.HTTP_201_CREATED,
    summary="Добавить комментарий к версии",
)
async def create_comment(
    version_id: uuid.UUID,
    dto: CreateCommentDTO,
    service: ReviewService = Depends(get_service(ReviewService)),
    user: AccessTokenPayload = Depends(require_role([RoleName.REVIEWER, RoleName.AUTHOR])),
):
    dto.article_version_id = version_id
    result = await service.create_comment(dto, user_id=user.id)
    return SuccessResponse(
        message="Comment added",
        data=result.model_dump(),
    )


# ── Assignment by version (for articles router) ────────────────


@article_reviews_router.get(
    "/{id}/versions/{version_id}/assignment",
    response_model=SuccessResponse[ReviewAssignmentFullPayload | None],
    summary="Назначение ревьюера для версии",
)
async def get_version_assignment(
    id: uuid.UUID,
    version_id: uuid.UUID,
    service: ReviewService = Depends(get_service(ReviewService)),
):
    result = await service.get_assignment_by_version(version_id)
    return SuccessResponse(data=result.model_dump() if result else None)
