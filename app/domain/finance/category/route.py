from __future__ import annotations
from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.pagination import CustomLimitOffsetPage
from app.core.security import get_current_user
from app.domain.finance.category.schema import CategorySchema
from app.domain.finance.category.service import CategoryService
from app.models import User
from app.shared.schemas import FilterPage

router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]


def category_service(session: Session) -> CategoryService:
    return CategoryService.from_session(session)


Service = Annotated[CategoryService, Depends(category_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def category_filter(
    page: int | None = None,
    name: str | None = None,
    limit: int | None = 12,
    offset: int | None = None,
    clean_cache: bool = False,
    with_deleted: bool = False,
) -> FilterPage:
    return FilterPage.build(
        page=page,
        name=name,
        limit=limit,
        offset=offset,
        clean_cache=clean_cache,
        with_deleted=with_deleted,
    )


@router.get(
    "",
    response_model=CustomLimitOffsetPage[CategorySchema] | list[CategorySchema],
    status_code=HTTPStatus.OK,
)
async def list_all(
    service: Service,
    current_user: CurrentUser,
    page_filter: Annotated[FilterPage, Depends(category_filter)],
):
    return await service.list(page_filter=page_filter, user=current_user)
