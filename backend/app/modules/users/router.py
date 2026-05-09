from fastapi import APIRouter, Depends
from app.core.responses import SuccessResponse

from app.core.deps import get_service
from app.modules.auth.schemas import (
    AccessTokenPayload
)
from app.core.dependencies import get_current_user
from .service import UserService

router = APIRouter()

@router.get(
    "/me",
    response_model=SuccessResponse
)
async def me(
    service: UserService = Depends(get_service(UserService)),
    user: AccessTokenPayload = Depends(get_current_user)
):
    payload = await service.get_user(user.id)
    return SuccessResponse("Fetched", data={"user": payload})