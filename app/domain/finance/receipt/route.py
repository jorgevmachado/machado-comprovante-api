from __future__ import annotations
from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import get_current_user
from app.domain.finance.receipt.schema import UploadReceiptResponseSchema, ReceiptSchema
from app.domain.finance.receipt.service import ReceiptService
from app.models import User

router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]


def receipt_service(session: Session) -> ReceiptService:
    return ReceiptService.from_session(session)


Service = Annotated[ReceiptService, Depends(receipt_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]


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

@router.get(
    "/{receipt_id}",
    response_model=ReceiptSchema,
    status_code=HTTPStatus.OK
)
async def get_receipt(
    service: Service,
    receipt_id: str,
    current_user: CurrentUser,
):
    return await service.get_receipt(receipt_id=receipt_id, user=current_user)