import uuid
from fastapi import APIRouter, Depends
from app.core.responses import SuccessResponse

from app.core.deps import get_service
from app.modules.auth.schemas import (
    AccessTokenPayload
)
from app.core.dependencies import get_current_user

from .service import UserService
from .schemas import (
    UserFiltersDTO,
    ProfileEditDTO
)

router = APIRouter()

@router.get(
    "/me",
    response_model=SuccessResponse
)
async def me(
    service: UserService = Depends(get_service(UserService)),
    user: AccessTokenPayload = Depends(get_current_user)
):
    result = await service.get_user(user.id)
    return SuccessResponse(data=result.model_dump())

@router.get(
    "/",
    response_model=SuccessResponse
)
async def get_users(
    filters: UserFiltersDTO = Depends(),
    service: UserService = Depends(get_service(UserService)),
):
    items, meta = await service.get_users(filters)
    return SuccessResponse(
        data=[item.model_dump() for item in items],
        meta=meta.model_dump(),
    )

@router.get(
    "/{id}",
    response_model=SuccessResponse
)
async def get_user(
    id: uuid.UUID,
    service: UserService = Depends(get_service(UserService)),
):
    result = await service.get_user(id)
    return SuccessResponse(data=result.model_dump())

@router.put(
    "/{id}",
    response_model=SuccessResponse
)
async def edit_profile(
    id: uuid.UUID,
    dto: ProfileEditDTO,
    user: AccessTokenPayload = Depends(get_current_user),
    service: UserService = Depends(get_service(UserService)),
):
    result = await service.edit_profile(id, dto, role=user.role)
    return SuccessResponse(
        message="Profile updated",
        data=result.model_dump(),
    )