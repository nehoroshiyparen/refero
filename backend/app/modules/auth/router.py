from fastapi import APIRouter, Depends, Request, Response, Cookie, status
from app.core.responses import SuccessResponse
from .schemas import (
    RegisterDTO,
    LoginDTO,
    AccessTokenPayload
)
from app.core.deps import get_service
from app.core.dependencies import (
    get_current_user, 
    get_refresh_token,
    unathorized_only
)
from .service import AuthService

router = APIRouter()

@router.post(
    "/register",
    response_model=SuccessResponse
)
async def register(
    dto: RegisterDTO,
    res: Response,
    service: AuthService = Depends(get_service(AuthService)),
    is_authorized: None = Depends(unathorized_only)
):
    payload = await service.register(dto)
    
    res.set_cookie(
        key="refresh_token",
        value=payload.refresh_token.token_hash,
        httponly=True,
        samesite="lax",
        expires=payload.refresh_token.expires_at 
    )

    return SuccessResponse(message="User created", data={"access_token": payload.access_token})

@router.post(
    "/login",
    response_model=SuccessResponse
)
async def login(
    dto: LoginDTO,
    res: Response,
    service: AuthService = Depends(get_service(AuthService)),
    is_authorized: None = Depends(unathorized_only)
):
    payload = await service.login(dto)

    res.set_cookie(
        key="refresh_token",
        value=payload.refresh_token.token_hash,
        httponly=True,
        samesite="lax",
        expires=payload.refresh_token.expires_at 
    )

    return SuccessResponse(message="Authorization complete", data={"access_token": payload.access_token})

@router.post(
    "/logout",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
async def logout(
    res: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_service(AuthService)),
    user: AccessTokenPayload = Depends(get_current_user)
):
    await service.logout(refresh_token)
    res.delete_cookie("refresh_token")
    return

@router.post(
    "/refresh",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    refresh_token: str = Depends(get_refresh_token),
    service: AuthService = Depends(get_service(AuthService))
): 
    access_token = await service.refresh(refresh_token)
    return SuccessResponse(message="Refreshed", data={"access_token": access_token})