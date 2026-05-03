from fastapi import APIRouter, Depends, Request, Response, Cookie, status
from app.core.responses import SuccessResponse
from .schemas import (
    RegisterRequest,
    LoginRequest
)
from app.core.deps import get_service
from .service import AuthService

router = APIRouter

@router.post(
    "/register",
    response_model=SuccessResponse
)
async def register(
    req: RegisterRequest, # Поменять на DTO
    res: Response,
    service: AuthService = Depends(get_service(AuthService))
):
    payload = await service.register(req)
    
    res.set_cookie(
        key="refresh_token",
        value=payload.refresh_token.token_hash,
        httponly=True,
        samesite="lax",
        max_age=payload.refresh_token.expires_at # скорее всего ошибка и нужно поправить
    )

    return SuccessResponse(message="User created", data={"access_token": payload.access_token})

@router.post(
    "/login",
    response_model=None
)
async def login(
    request: LoginRequest,
    service: AuthService = Depends(get_service(AuthService))
):
    payload = await service.login(request)
    return 

@router.post(
    "/logout",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
async def logout(
    res: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_service(AuthService))
):
    response = await service.logout(refresh_token)
    return response

@router.post(
    "/refresh",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
async def refresh(
    res: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_service(AuthService))
): 
    response = await service.refresh(refresh_token)
    return response