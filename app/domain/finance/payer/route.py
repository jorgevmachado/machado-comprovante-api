from __future__ import annotations
from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.pagination import CustomLimitOffsetPage
from app.core.security import get_current_user
from app.domain.finance.payer.schema import PayerSchema, PayerPersistSchema
from app.domain.finance.payer.service import PayerService
from app.models import User
from app.shared.schemas import FilterPage

router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]


def payer_service(session: Session) -> PayerService:
    return PayerService.from_session(session)


Service = Annotated[PayerService, Depends(payer_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def payer_filter(
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
    response_model=CustomLimitOffsetPage[PayerSchema] | list[PayerSchema],
    status_code=HTTPStatus.OK,
)
async def list_all(
    service: Service,
    current_user: CurrentUser,
    page_filter: Annotated[FilterPage, Depends(payer_filter)],
):
    return await service.list(page_filter=page_filter, user=current_user)


@router.get("/{param}", response_model=PayerSchema, status_code=HTTPStatus.OK)
async def find_one(param: str, service: Service, current_user: CurrentUser):
    return await service.find_by(
        id=param,
        user_request=current_user.username,
        user_id=str(current_user.id),
    )


@router.post(
    "",
    response_model=PayerSchema,
    status_code=HTTPStatus.CREATED,
)
async def create(
    service: Service,
    current_user: CurrentUser,
    payload: PayerPersistSchema,
):
    return await service.create(
        user_id=current_user.id, name=payload.name
    )


@router.put(
    "/{payer_id}",
    response_model=PayerSchema,
    status_code=HTTPStatus.OK,
)
async def update(
    service: Service,
    payer_id: str,
    current_user: CurrentUser,
    payload: PayerPersistSchema,
):
    return await service.update(
        param=payer_id, update_schema=payload, user_request=current_user.username
    )
