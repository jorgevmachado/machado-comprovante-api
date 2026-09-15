from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.finance.beneficiary.service import BeneficiaryService
from app.domain.finance.institution.service import InstitutionService
from app.domain.finance.payment.service import PaymentService
from app.domain.finance.receipt.service import ReceiptService
from app.domain.finance.schema import FinanceConfirmRequestSchema
from app.domain.finance.service import FinanceService
from app.models.enums import ProcessingStatusEnum


def build_confirm_payload() -> FinanceConfirmRequestSchema:
    return FinanceConfirmRequestSchema(
        paid_amount=Decimal("387.42"),
        payment_date=date(2026, 9, 12),
        beneficiary="Empresa Exemplo",
        source_institution="Banco Exemplo",
        destination_institution="Banco Destino",
    )


class TestFinanceService:
    @staticmethod
    def test_builds_services_from_session():
        session = AsyncMock()

        service = FinanceService(session)

        assert isinstance(service.receipt_service, ReceiptService)
        assert isinstance(service.payment_service, PaymentService)
        assert isinstance(service.beneficiary_service, BeneficiaryService)
        assert isinstance(service.institution_service, InstitutionService)

    @staticmethod
    @pytest.mark.asyncio
    async def test_confirm_creates_payment_and_returns_response():
        session = AsyncMock()

        receipt_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            receipt_service=receipt_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            institution_service=institution_service,
        )

        user = SimpleNamespace(
            id=uuid4(),
        )

        receipt = SimpleNamespace(
            id=uuid4(),
            processing_status=ProcessingStatusEnum.PROCESSED,
        )

        beneficiary = SimpleNamespace(
            id=uuid4(),
            name="Empresa Exemplo",
        )

        source_institution = SimpleNamespace(
            id=uuid4(),
            name="Banco Exemplo",
        )

        destination_institution = SimpleNamespace(
            id=uuid4(),
            name="Banco Destino",
        )

        payment = SimpleNamespace(
            id=uuid4(),
            amount=Decimal("387.42"),
            payment_date=date(2026, 9, 12),
        )

        receipt_service.validate_confirm_receipt.return_value = receipt
        beneficiary_service.resolve.return_value = beneficiary

        institution_service.resolve.side_effect = [
            source_institution,
            destination_institution,
        ]

        payment_service.create.return_value = payment

        payload = build_confirm_payload()

        result = await service.confirm(
            receipt_id=str(receipt.id),
            payload=payload,
            user=user,
        )

        assert result.beneficiary.id == beneficiary.id
        assert result.beneficiary.name == beneficiary.name

        assert result.payment.id == payment.id
        assert result.payment.amount == payment.amount
        assert result.payment.payment_date == payment.payment_date

        assert result.source_institution.id == source_institution.id
        assert result.source_institution.name == source_institution.name

        assert result.destination_institution is not None
        assert result.destination_institution.id == destination_institution.id
        assert result.destination_institution.name == destination_institution.name

        receipt_service.validate_confirm_receipt.assert_awaited_once_with(
            receipt_id=str(receipt.id),
            user=user,
        )

        payment_service.check_receipt.assert_awaited_once_with(
            receipt_id=receipt.id,
            user=user,
        )

        beneficiary_service.resolve.assert_awaited_once_with(
            name=payload.beneficiary,
        )

        assert institution_service.resolve.await_count == 2
        institution_service.resolve.assert_any_await(
            name=payload.source_institution,
        )
        institution_service.resolve.assert_any_await(
            name=payload.destination_institution,
        )

        payment_service.create.assert_awaited_once_with(
            amount=payload.paid_amount,
            user_id=user.id,
            receipt_id=receipt.id,
            payment_date=payload.payment_date,
            beneficiary_id=beneficiary.id,
            source_institution_id=source_institution.id,
            destination_institution_id=destination_institution.id,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_confirm_does_not_resolve_destination_when_not_provided():
        session = AsyncMock()

        receipt_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            receipt_service=receipt_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            institution_service=institution_service,
        )

        user = SimpleNamespace(
            id=uuid4(),
        )

        receipt = SimpleNamespace(
            id=uuid4(),
        )

        beneficiary = SimpleNamespace(
            id=uuid4(),
            name="Empresa Exemplo",
        )

        source_institution = SimpleNamespace(
            id=uuid4(),
            name="Banco Exemplo",
        )

        payment = SimpleNamespace(
            id=uuid4(),
            amount=Decimal("95.00"),
            payment_date=date(2026, 9, 12),
        )

        receipt_service.validate_confirm_receipt.return_value = receipt
        beneficiary_service.resolve.return_value = beneficiary
        institution_service.resolve.return_value = source_institution
        payment_service.create.return_value = payment

        payload = FinanceConfirmRequestSchema(
            paid_amount=Decimal("95.00"),
            payment_date=date(2026, 9, 12),
            beneficiary="Empresa Exemplo",
            source_institution="Banco Exemplo",
            destination_institution=None,
        )

        result = await service.confirm(
            receipt_id=str(receipt.id),
            payload=payload,
            user=user,
        )

        assert result.destination_institution is None

        institution_service.resolve.assert_awaited_once_with(
            name=payload.source_institution,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_confirm_reraises_dependency_error():
        session = AsyncMock()
        receipt_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            receipt_service=receipt_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            institution_service=institution_service,
        )

        receipt_service.validate_confirm_receipt.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            await service.confirm(
                receipt_id="receipt-id",
                payload=build_confirm_payload(),
                user=SimpleNamespace(id=uuid4()),
            )

        payment_service.create.assert_not_awaited()
