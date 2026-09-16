from __future__ import annotations

from datetime import date
from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.pagination import CustomLimitOffsetPage
from app.core.security import get_current_user
from app.domain.finance.payment.schema import PaymentSchema
from app.domain.finance.payment.service import PaymentService
from app.models import User
from app.shared.schemas import FilterPage

router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]


def payment_service(session: Session) -> PaymentService:
    return PaymentService.from_session(session)


Service = Annotated[PaymentService, Depends(payment_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def payment_filter(
    page: int | None = None,
    limit: int | None = 12,
    offset: int | None = None,
    order_by: str | None = None,
    end_date: date | None = None,
    start_date: date | None = None,
    clean_cache: bool = False,
    institution: str | None = None,
    beneficiary: str | None = None,
    with_deleted: bool = False,
    source_institution: str | None = None,
    destination_institution: str | None = None,
) -> FilterPage:
    return FilterPage.build(
        page=page,
        limit=limit,
        offset=offset,
        order_by=order_by,
        end_date=end_date,
        start_date=start_date,
        clean_cache=clean_cache,
        institution=institution,
        beneficiary=beneficiary,
        with_deleted=with_deleted,
        source_institution=source_institution,
        destination_institution=destination_institution,
    )


@router.get(
    "",
    response_model=CustomLimitOffsetPage[PaymentSchema] | list[PaymentSchema],
    status_code=HTTPStatus.OK,
)
async def list_all(
    service: Service,
    current_user: CurrentUser,
    page_filter: Annotated[FilterPage, Depends(payment_filter)],
):
    return await service.list(page_filter=page_filter, user=current_user)
