from fastapi import APIRouter, Depends, Request, Response, Cookie, status
from app.core.responses import SuccessResponse

from .schemas import (
    ArticleUpdateDTO,
    ArticleCreateDTO,
    ArticleFiltersDTO
)

router = APIRouter()

@router.get(
    "/",
    response_model=SuccessResponse
)
async def get_articles(
    filters: ArticleFiltersDTO = Depends(),
):
    pass

@router.get(
    "/{id}",
    response_model=SuccessResponse
)
async def get_article_by_id(id: int):
    pass

@router.post(
    "/",
    response_model=SuccessResponse
)
async def create_article(
    dto: ArticleCreateDTO,
):
    pass

@router.put(
    "/{id}",
    response_model=SuccessResponse
)
async def update_article(
    id: int, 
    dto: ArticleUpdateDTO
):
    pass

@router.delete(
    "/{id}",
    response_model=SuccessResponse
)
async def delete_article(
    id: int,
):
    pass

@router.post(
    "/{id}/submit-for-approval",
    response_model=SuccessResponse
)
async def submit_for_approval(id: int):
    pass

@router.post(
    "/{id}/authors",
    response_model=SuccessResponse
)
async def add_author(id: int):
    pass

@router.delete(
    "/{id}/authors",
    response_model=SuccessResponse
)
async def delete_author(id: int):
    pass

@router.get(
    "/{id}/download",
    response_model=SuccessResponse
)
async def download_article(id: int):
    pass