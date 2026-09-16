from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.domain.finance.payment.service import PaymentService
from app.models import Payment
from app.shared.schemas import FilterPage


class TestPaymentService:
    @staticmethod
    def test_from_session_builds_service():
        service = PaymentService.from_session(AsyncMock())

        assert isinstance(service, PaymentService)

    @staticmethod
    @pytest.mark.asyncio
    async def test_check_receipt_does_not_raise_when_payment_does_not_exist():
        service = PaymentService(AsyncMock())
        service.find_by = AsyncMock(return_value=None)

        receipt_id = uuid4()
        user = SimpleNamespace(id=uuid4())

        await service.check_receipt(
            receipt_id=receipt_id,
            user=user,
        )

        service.find_by.assert_awaited_once_with(
            receipt_id=receipt_id,
            user_id=str(user.id),
            without_throw=True,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_check_receipt_raises_when_payment_already_exists():
        service = PaymentService(AsyncMock())
        service.find_by = AsyncMock(return_value=SimpleNamespace(id=uuid4()))

        receipt_id = uuid4()
        user = SimpleNamespace(id=uuid4())

        with pytest.raises(
                Exception,
                match="Payment already exists for the given receipt and user.",
        ):
            await service.check_receipt(
                receipt_id=receipt_id,
                user=user,
            )

        service.find_by.assert_awaited_once_with(
            receipt_id=receipt_id,
            user_id=str(user.id),
            without_throw=True,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_create_builds_and_saves_payment():
        repository = AsyncMock()
        service = PaymentService(repository)

        user_id = uuid4()
        receipt_id = uuid4()
        beneficiary_id = uuid4()
        source_institution_id = uuid4()
        destination_institution_id = uuid4()

        amount = Decimal("387.42")
        payment_date = date(2026, 9, 12)

        expected = SimpleNamespace(id=uuid4())
        repository.save.return_value = expected

        result = await service.create(
            user_id=user_id,
            receipt_id=receipt_id,
            amount=amount,
            payment_date=payment_date,
            beneficiary_id=beneficiary_id,
            source_institution_id=source_institution_id,
            destination_institution_id=destination_institution_id,
        )

        assert result is expected

        repository.save.assert_awaited_once()

        payment = repository.save.await_args.kwargs["entity"]

        assert isinstance(payment, Payment)
        assert payment.amount == amount
        assert payment.user_id == user_id
        assert payment.receipt_id == receipt_id
        assert payment.payment_date == payment_date
        assert payment.beneficiary_id == beneficiary_id
        assert payment.source_institution_id == source_institution_id
        assert payment.destination_institution_id == destination_institution_id

    @staticmethod
    @pytest.mark.asyncio
    async def test_create_allows_destination_institution_to_be_none():
        repository = AsyncMock()
        service = PaymentService(repository)

        user_id = uuid4()
        receipt_id = uuid4()
        beneficiary_id = uuid4()
        source_institution_id = uuid4()

        repository.save.return_value = SimpleNamespace(id=uuid4())

        await service.create(
            user_id=user_id,
            receipt_id=receipt_id,
            amount=Decimal("95.00"),
            payment_date=date(2026, 9, 12),
            beneficiary_id=beneficiary_id,
            source_institution_id=source_institution_id,
            destination_institution_id=None,
        )

        repository.save.assert_awaited_once()

        payment = repository.save.await_args.kwargs["entity"]

        assert payment.destination_institution_id is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_returns_repository_result():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        page_filter = FilterPage.build(
            beneficiary="Amazon",
        )

        expected = [
            SimpleNamespace(id=uuid4()),
            SimpleNamespace(id=uuid4()),
        ]

        repository.list.return_value = expected

        result = await service.list(
            user=user,
            page_filter=page_filter,
        )

        assert result is expected

        repository.list.assert_awaited_once_with(
            user_id=user.id,
            page_filter=page_filter,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_returns_exception_pagination_when_repository_raises():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        page_filter = FilterPage.build(
            page=1,
            limit=10,
        )

        exception = Exception("Repository error")
        repository.list.side_effect = exception

        expected = SimpleNamespace(
            items=[],
            total=0,
        )

        with (
            patch(
                "app.domain.finance.payment.service.handle_service_exception"
            ) as handle_exception,
            patch(
                "app.domain.finance.payment.service.exception_pagination",
                return_value=expected,
            ) as pagination,
        ):
            result = await service.list(
                user=user,
                page_filter=page_filter,
            )

        assert result is expected

        repository.list.assert_awaited_once_with(
            user_id=user.id,
            page_filter=page_filter,
        )

        handle_exception.assert_called_once_with(
            exception,
            logger=service.logger_params.logger,
            service=service.logger_params.service,
            operation="list",
            user_request=user.username,
            raise_exception=False,
        )

        pagination.assert_called_once_with(page_filter)

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_returns_exception_pagination_when_repository_raises_without_filter():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        exception = Exception("Repository error")
        repository.list.side_effect = exception

        expected = SimpleNamespace(
            items=[],
            total=0,
        )

        with (
            patch("app.domain.finance.payment.service.handle_service_exception"),
            patch(
                "app.domain.finance.payment.service.exception_pagination",
                return_value=expected,
            ) as pagination,
        ):
            result = await service.list(
                user=user,
                page_filter=None,
            )

        assert result is expected

        repository.list.assert_awaited_once_with(
            user_id=user.id,
            page_filter=None,
        )

        pagination.assert_called_once_with(None)

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_logs_success_after_repository_call():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        expected = []

        repository.list.return_value = expected

        with patch(
            "app.domain.finance.payment.service.log_service_success"
        ) as log_success:
            result = await service.list(
                user=user,
                page_filter=None,
            )

        assert result is expected

        log_success.assert_called_once_with(
            service.logger_params,
            operation="list",
            message="List successfully",
            user_request=user.username,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_logs_success_even_when_repository_raises():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        exception = Exception("Repository error")
        repository.list.side_effect = exception

        expected = SimpleNamespace(
            items=[],
            total=0,
        )

        with (
            patch("app.domain.finance.payment.service.handle_service_exception"),
            patch(
                "app.domain.finance.payment.service.exception_pagination",
                return_value=expected,
            ),
            patch(
                "app.domain.finance.payment.service.log_service_success"
            ) as log_success,
        ):
            result = await service.list(
                user=user,
                page_filter=None,
            )

        assert result is expected

        log_success.assert_called_once_with(
            service.logger_params,
            operation="list",
            message="List successfully",
            user_request=user.username,
        )
