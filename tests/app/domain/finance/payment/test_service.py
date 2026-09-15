from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.finance.payment.service import PaymentService
from app.models import Payment


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
