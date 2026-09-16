from __future__ import annotations

from typing import Annotated
from fastapi import Depends, APIRouter
from http import HTTPStatus

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.core.database import get_session
from app.domain.finance.schema import (
    FinanceConfirmRequestSchema,
    FinanceConfirmResponseSchema,
)
from app.domain.finance.service import FinanceService
from app.domain.finance.receipt.route import router as receipt_router
from app.domain.finance.beneficiary.route import router as beneficiary_router
from app.domain.finance.institution.route import router as institution_router
from app.models import User

Session = Annotated[AsyncSession, Depends(get_session)]


def finance_service(session: Session) -> FinanceService:
    return FinanceService(session)


Service = Annotated[FinanceService, Depends(finance_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()

router.include_router(receipt_router, prefix="/receipt", tags=["Receipt"])

router.include_router(beneficiary_router, prefix="/beneficiary", tags=["Beneficiary"])

router.include_router(institution_router, prefix="/institution", tags=["Institution"])


@router.post(
    "/receipt/{receipt_id}/confirm",
    response_model=FinanceConfirmResponseSchema,
    status_code=HTTPStatus.CREATED,
)
async def confirm(
    receipt_id: str,
    service: Service,
    payload: FinanceConfirmRequestSchema,
    current_user: CurrentUser,
):
    return await service.confirm(
        receipt_id=receipt_id, payload=payload, user=current_user
    )
