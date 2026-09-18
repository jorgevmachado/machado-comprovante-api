from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import handle_service_exception
from app.core.logging import LoggingParams, log_service_success
from app.core.pagination import exception_pagination
from app.core.service import BaseService
from app.domain.finance.payment.repository import PaymentRepository
from app.domain.finance.payment.schema import PaymentSchema, PaymentSummaryMinMaxSchema

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
            return await self.repository.list(user_id=user.id, page_filter=page_filter)
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

    async def summary_count(
        self,
        user: User,
        page_filter: Annotated[FilterPage, Query()] | None = None,
    ):
        try:
            return await self.repository.summary_count(
                user_id=user.id, page_filter=page_filter
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation="summary_count",
                user_request=user.username,
                raise_exception=False,
            )
        finally:
            log_service_success(
                self.logger_params,
                operation="summary_count",
                message="Summary count successfully",
                user_request=user.username,
            )

    async def summary_total(
        self,
        user: User,
        page_filter: Annotated[FilterPage, Query()] | None = None,
    ):
        try:
            return await self.repository.summary_total(
                user_id=user.id, page_filter=page_filter
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation="summary_total",
                user_request=user.username,
                raise_exception=False,
            )
        finally:
            log_service_success(
                self.logger_params,
                operation="summary_total",
                message="Summary total successfully",
                user_request=user.username,
            )

    async def summary_max(
        self,
        user: User,
        page_filter: Annotated[FilterPage, Query()] | None = None,
    ):
        try:
            result = await self.repository.summary_order_by(
                user_id=user.id, order_by="desc", page_filter=page_filter
            )
            return PaymentSummaryMinMaxSchema(payment=result)
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation="summary_max",
                user_request=user.username,
                raise_exception=False,
            )
        finally:
            log_service_success(
                self.logger_params,
                operation="summary_max",
                message="Summary max successfully",
                user_request=user.username,
            )

    async def summary_min(
        self,
        user: User,
        page_filter: Annotated[FilterPage, Query()] | None = None,
    ):
        try:
            result = await self.repository.summary_order_by(
                user_id=user.id, order_by="asc", page_filter=page_filter
            )
            return PaymentSummaryMinMaxSchema(payment=result)
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation="summary_min",
                user_request=user.username,
                raise_exception=False,
            )
        finally:
            log_service_success(
                self.logger_params,
                operation="summary_min",
                message="Summary min successfully",
                user_request=user.username,
            )

    @staticmethod
    def _validate_beneficiary_filter(
        page_filter: Annotated[FilterPage, Query()] | None = None,
    ) -> str:
        error_message = "The beneficiary query parameter is required for the query"
        if not page_filter:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=error_message,
            )
        raw_filters = page_filter.model_dump(exclude_none=True)
        param = raw_filters.get("beneficiary")
        if not param:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=error_message,
            )
        return param

    async def summary_beneficiary(
        self,
        user: User,
        page_filter: Annotated[FilterPage, Query()] | None = None,
    ):
        beneficiary = self._validate_beneficiary_filter(page_filter)
        try:
            return await self.repository.summary_beneficiary(
                user_id=user.id, beneficiary=beneficiary, page_filter=page_filter
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation="summary_beneficiary",
                user_request=user.username,
                raise_exception=False,
            )
        finally:
            log_service_success(
                self.logger_params,
                operation="summary_beneficiary",
                message="Summary beneficiary successfully",
                user_request=user.username,
            )
