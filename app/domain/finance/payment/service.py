from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import handle_service_exception
from app.core.logging import LoggingParams, log_service_success
from app.core.pagination import exception_pagination
from app.core.service import BaseService
from app.domain.finance.payment.repository import PaymentRepository
from app.domain.finance.payment.schema import PaymentSchema

from app.models import Payment, User
from app.shared.schemas import FilterPage

logger = logging.getLogger(__name__)


class PaymentService(BaseService[PaymentRepository, Payment]):
    def __init__(self, repository: PaymentRepository) -> None:
        super().__init__(
            alias="Payment",
            repository=repository,
            logger_params=LoggingParams(
                logger=logger, service="PaymentService", operation="payment"
            ),
            schema_class=PaymentSchema,
            cache_prefix="payment",
        )

    @classmethod
    def from_session(cls, session: AsyncSession) -> PaymentService:
        return cls(PaymentRepository(session))

    async def check_receipt(self, receipt_id: UUID, user: User):
        payment = await self.find_by(
            receipt_id=receipt_id, user_id=str(user.id), without_throw=True
        )
        if payment:
            raise Exception("Payment already exists for the given receipt and user.")

    async def create(
        self,
        user_id: UUID,
        receipt_id: UUID,
        amount: Decimal,
        payment_date: date,
        beneficiary_id: UUID,
        source_institution_id: UUID,
        destination_institution_id: UUID | None,
    ) -> Payment:
        payment = Payment(
            amount=amount,
            user_id=user_id,
            receipt_id=receipt_id,
            payment_date=payment_date,
            beneficiary_id=beneficiary_id,
            source_institution_id=source_institution_id,
            destination_institution_id=destination_institution_id,
        )
        return await self.repository.save(entity=payment)

    async def list(
        self,
        user: User,
        page_filter: Annotated[FilterPage, Query()] | None = None,
    ):
        try:
            return await self.repository.list(
                user_id=user.id, page_filter=page_filter
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation="list",
                user_request=user.username,
                raise_exception=False,
            )
            return exception_pagination(page_filter)
        finally:
            log_service_success(
                self.logger_params,
                operation="list",
                message="List successfully",
                user_request=user.username,
            )
