from __future__ import annotations
from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.pagination import CustomLimitOffsetPage
from app.core.security import get_current_user
from app.domain.finance.receipt.schema import (
    UploadReceiptResponseSchema,
    ReceiptSchema,
    BatchReceiptResponseSchema,
)
from app.domain.finance.receipt.service import ReceiptService
from app.domain.finance.schema import FinanceConfirmRequestSchema
from app.models import User
from app.shared.schemas import FilterPage

router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]


def receipt_service(session: Session) -> ReceiptService:
    return ReceiptService.from_session(session)


Service = Annotated[ReceiptService, Depends(receipt_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]

def receipt_filter(
    page: int | None = None,
    limit: int | None = 12,
    offset: int | None = None,
    order_by: str | None = None,
    clean_cache: bool = False,
    with_deleted: bool = False,
) -> FilterPage:
    return FilterPage.build(
        page=page,
        limit=limit,
        offset=offset,
        order_by=order_by,
        clean_cache=clean_cache,
        with_deleted=with_deleted,
    )

@router.get(
    "",
    response_model=CustomLimitOffsetPage[ReceiptSchema] | list[ReceiptSchema],
    status_code=HTTPStatus.OK,
)
async def list_all(
    service: Service,
    current_user: CurrentUser,
    page_filter: FilterPage = Depends(receipt_filter),
):
    return await service.list_all(page_filter=FilterPage.build(
        user_id=current_user.id,
        page_filter=page_filter,
    ),
    user_request=current_user.username)

@router.post(
    "/upload",
    response_model=UploadReceiptResponseSchema,
    status_code=HTTPStatus.CREATED,
)
async def received_receipt(
    service: Service,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    return await service.received_receipt(file=file, user=current_user)


@router.post(
    "/batch", response_model=BatchReceiptResponseSchema, status_code=HTTPStatus.CREATED
)
async def received_receipt_batch(
    files: Annotated[list[UploadFile], File(...)],
    current_user: CurrentUser,
    service: Service,
):
    return await service.received_receipt_batch(files=files, user=current_user)


@router.get("/{receipt_id}", response_model=ReceiptSchema, status_code=HTTPStatus.OK)
async def get_receipt(
    service: Service,
    receipt_id: str,
    current_user: CurrentUser,
):
    return await service.get_receipt(receipt_id=receipt_id, user=current_user)


@router.put("/{receipt_id}", response_model=ReceiptSchema, status_code=HTTPStatus.OK)
async def update_receipt(
    service: Service,
    receipt_id: str,
    payload: FinanceConfirmRequestSchema,
    current_user: CurrentUser,
):
    return await service.update_receipt(
        receipt_id=receipt_id, payload=payload.model_dump(mode="json"), user=current_user
    )