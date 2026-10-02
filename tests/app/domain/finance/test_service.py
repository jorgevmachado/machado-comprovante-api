from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, call
from uuid import uuid4

import pytest

from app.domain.finance.beneficiary.service import BeneficiaryService
from app.domain.finance.category.service import CategoryService
from app.domain.finance.institution.service import InstitutionService
from app.domain.finance.payment.service import PaymentService
from app.domain.finance.receipt.service import ReceiptService
from app.domain.finance.schema import (
    FinanceConfirmRequestSchema,
    FinanceUpdatePaymentRequestSchema,
)
from app.domain.finance.service import FinanceService
from app.models import utcnow
from app.models.enums import ProcessingStatusEnum


def build_confirm_payload() -> FinanceConfirmRequestSchema:
    return FinanceConfirmRequestSchema(
        paid_amount=Decimal("387.42"),
        payment_date=date(2026, 9, 12),
        category="Categoria Exemplo",
        beneficiary="Empresa Exemplo",
        source_institution="Banco Exemplo",
        destination_institution="Banco Destino",
    )


class TestFinanceService:
    @staticmethod
    def test_builds_services_from_session():
        session = AsyncMock()

        service = FinanceService(session)

        assert isinstance(service.category_service, CategoryService)
        assert isinstance(service.receipt_service, ReceiptService)
        assert isinstance(service.payment_service, PaymentService)
        assert isinstance(service.beneficiary_service, BeneficiaryService)
        assert isinstance(service.institution_service, InstitutionService)


class TestFinanceServiceConfirm:
    @staticmethod
    @pytest.mark.asyncio
    async def test_confirm_creates_payment_and_returns_response():
        session = AsyncMock()

        receipt_service = AsyncMock()
        payment_service = AsyncMock()
        category_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            receipt_service=receipt_service,
            payment_service=payment_service,
            category_service=category_service,
            beneficiary_service=beneficiary_service,
            institution_service=institution_service,
        )

        user = SimpleNamespace(
            id=uuid4(),
        )

        receipt = SimpleNamespace(
            id=uuid4(),
            created_at=utcnow(),
            updated_at=None,
            deleted_at=None,
            file_name="receipt.pdf",
            file_type="application/pdf",
            file_size=1024,
            extracted_data=None,
            processing_status=ProcessingStatusEnum.PROCESSED,
        )

        category = SimpleNamespace(
            id=uuid4(),
            name="Categoria Exemplo",
            created_at=utcnow(),
        )

        beneficiary = SimpleNamespace(
            id=uuid4(),
            name="Empresa Exemplo",
            created_at=utcnow(),
        )

        source_institution = SimpleNamespace(
            id=uuid4(),
            name="Banco Exemplo",
            created_at=utcnow(),
        )

        destination_institution = SimpleNamespace(
            id=uuid4(),
            name="Banco Destino",
            created_at=utcnow(),
        )

        payment = SimpleNamespace(
            id=uuid4(),
            amount=Decimal("387.42"),
            created_at=utcnow(),
            payment_date=date(2026, 9, 12),
        )

        receipt_service.validate_confirm_receipt.return_value = receipt
        receipt_service.confirm_receipt.return_value = receipt

        category_service.resolve.return_value = category

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

        assert result.category.id == category.id
        assert result.category.name == category.name

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

        category_service.resolve.assert_awaited_once_with(
            name=payload.category,
            user_id=user.id,
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
            category_id=category.id,
            description=None,
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
        category_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            receipt_service=receipt_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            category_service=category_service,
            institution_service=institution_service,
        )

        user = SimpleNamespace(
            id=uuid4(),
        )

        category = SimpleNamespace(
            id=uuid4(),
            name="Categoria Exemplo",
            created_at=utcnow(),
        )

        receipt = SimpleNamespace(
            id=uuid4(),
            updated_at=None,
            deleted_at=None,
            created_at=utcnow(),
            file_name="receipt.pdf",
            file_type="application/pdf",
            file_size=1024,
            extracted_data=None,
            processing_status=ProcessingStatusEnum.PROCESSED,
        )

        beneficiary = SimpleNamespace(
            id=uuid4(),
            name="Empresa Exemplo",
            created_at=utcnow(),
        )

        source_institution = SimpleNamespace(
            id=uuid4(),
            name="Banco Exemplo",
            created_at=utcnow(),
        )

        payment = SimpleNamespace(
            id=uuid4(),
            amount=Decimal("95.00"),
            created_at=utcnow(),
            payment_date=date(2026, 9, 12),
        )

        receipt_service.validate_confirm_receipt.return_value = receipt
        receipt_service.confirm_receipt.return_value = receipt
        beneficiary_service.resolve.return_value = beneficiary
        category_service.resolve.return_value = category
        institution_service.resolve.return_value = source_institution
        payment_service.create.return_value = payment

        payload = FinanceConfirmRequestSchema(
            paid_amount=Decimal("95.00"),
            payment_date=date(2026, 9, 12),
            category="Categoria Exemplo",
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
        category_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            receipt_service=receipt_service,
            category_service=category_service,
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


class TestFinanceServiceUpdatePayment:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_payment_and_receipt_with_all_fields():
        session = AsyncMock()
        receipt_service = AsyncMock()
        category_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            receipt_service=receipt_service,
            category_service=category_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            institution_service=institution_service,
        )

        user = SimpleNamespace(id=uuid4())
        payment_id = uuid4()
        payload = FinanceUpdatePaymentRequestSchema(
            payer="New Payer",
            amount=Decimal("150.00"),
            category="New Category",
            beneficiary="New Beneficiary",
            payment_date=date(2026, 9, 15),
            source_institution="New Source Bank",
            destination_institution="New Destination Bank",
        )

        payment_service.find_by.return_value = SimpleNamespace(id=payment_id)

        category = SimpleNamespace(
            id=uuid4(),
            name="New Category",
            created_at=utcnow(),
        )

        category_service.resolve.return_value = category

        beneficiary = SimpleNamespace(
            id=uuid4(),
            name="New Beneficiary",
            created_at=utcnow(),
        )

        beneficiary_service.resolve.return_value = beneficiary

        source_institution = SimpleNamespace(
            id=uuid4(),
            name="New Source Bank",
            created_at=utcnow(),
        )

        destination_institution = SimpleNamespace(
            id=uuid4(),
            name="New Destination Bank",
            created_at=utcnow(),
        )

        institution_service.resolve.side_effect = [
            source_institution,
            destination_institution,
        ]

        receipt = SimpleNamespace(
            id=uuid4(),
            created_at=utcnow(),
            updated_at=None,
            deleted_at=None,
            file_name="receipt.pdf",
            file_type="application/pdf",
            file_size=1024,
            extracted_data=None,
            processing_status=ProcessingStatusEnum.PROCESSED,
        )

        payment = SimpleNamespace(
            id=uuid4(),
            amount=Decimal("150.00"),
            receipt=receipt,
            category=category,
            beneficiary=beneficiary,
            source_institution=source_institution,
            destination_institution=destination_institution,
            created_at=utcnow(),
            payment_date=date(2026, 9, 15),
        )

        payment_service.update_payment.return_value = payment

        receipt_service.update_receipt_payment.return_value = receipt

        expected_payload = {
            "amount": payload.amount,
            "payment_date": payload.payment_date,
            "category_id": category.id,
            "beneficiary_id": beneficiary.id,
            "source_institution_id": source_institution.id,
            "destination_institution_id": destination_institution.id,
        }

        result = await service.update_payment(payment_id=str(payment_id), payload=payload, user=user)

        payment_service.find_by.assert_awaited_once_with(
            id=str(payment_id),
            user_id=str(user.id),
        )

        category_service.resolve.assert_awaited_once_with(
            user_id=user.id,
            name=payload.category,
        )

        beneficiary_service.resolve.assert_awaited_once_with(
            name=payload.beneficiary,
        )

        institution_service.resolve.assert_has_awaits([
            call(name=payload.source_institution),
            call(name=payload.destination_institution),
        ])

        payment_service.update_payment.assert_awaited_once_with(
            payment_id=str(payment_id),
            payload=expected_payload,
            user=user,
        )

        assert result is payment

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_payment_when_there_is_nothing_to_update():
        session = AsyncMock()
        receipt_service = AsyncMock()
        category_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            receipt_service=receipt_service,
            category_service=category_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            institution_service=institution_service,
        )

        user = SimpleNamespace(id=uuid4())
        payment_id = uuid4()
        payload = FinanceUpdatePaymentRequestSchema(
            payer=None,
            amount=None,
            category=None,
            beneficiary=None,
            payment_date=None,
            source_institution=None,
            destination_institution=None,
        )

        beneficiary = SimpleNamespace(
            id=uuid4(),
            name="New Beneficiary",
            created_at=utcnow(),
        )

        category = SimpleNamespace(
            id=uuid4(),
            name="New Category",
            created_at=utcnow(),
        )

        source_institution = SimpleNamespace(
            id=uuid4(),
            name="New Source Bank",
            created_at=utcnow(),
        )

        destination_institution = SimpleNamespace(
            id=uuid4(),
            name="New Destination Bank",
            created_at=utcnow(),
        )

        receipt = SimpleNamespace(
            id=uuid4(),
            created_at=utcnow(),
            updated_at=None,
            deleted_at=None,
            file_name="receipt.pdf",
            file_type="application/pdf",
            file_size=1024,
            extracted_data=None,
            processing_status=ProcessingStatusEnum.PROCESSED,
        )

        payment = SimpleNamespace(
            id=payment_id,
            amount=Decimal("150.00"),
            receipt=receipt,
            beneficiary=beneficiary,
            category=category,
            source_institution=source_institution,
            destination_institution=destination_institution,
            created_at=utcnow(),
            payment_date=date(2026, 9, 15),
        )

        payment_service.find_by.return_value = payment

        result = await service.update_payment(payment_id=str(payment_id), payload=payload, user=user)

        payment_service.find_by.assert_awaited_once_with(
            id=str(payment_id),
            user_id=str(user.id),
        )

        payment_service.update_payment.assert_not_awaited()
        receipt_service.update_receipt_payment.assert_not_awaited()
        category_service.resolve.assert_not_awaited()
        beneficiary_service.resolve.assert_not_awaited()
        institution_service.resolve.assert_not_awaited()

        assert result is payment

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_amount():
        session = AsyncMock()
        receipt_service = AsyncMock()
        category_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            receipt_service=receipt_service,
            category_service=category_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            institution_service=institution_service,
        )

        user = SimpleNamespace(id=uuid4())
        payment_id = uuid4()
        payload = FinanceUpdatePaymentRequestSchema(
            payer=None,
            amount=Decimal("150.00"),
            beneficiary=None,
            payment_date=None,
            source_institution=None,
            destination_institution=None,
        )

        category = SimpleNamespace(
            id=uuid4(),
            name="New Category",
            created_at=utcnow(),
        )

        beneficiary = SimpleNamespace(
            id=uuid4(),
            name="New Beneficiary",
            created_at=utcnow(),
        )

        source_institution = SimpleNamespace(
            id=uuid4(),
            name="New Source Bank",
            created_at=utcnow(),
        )

        destination_institution = SimpleNamespace(
            id=uuid4(),
            name="New Destination Bank",
            created_at=utcnow(),
        )

        receipt = SimpleNamespace(
            id=uuid4(),
            created_at=utcnow(),
            updated_at=None,
            deleted_at=None,
            file_name="receipt.pdf",
            file_type="application/pdf",
            file_size=1024,
            extracted_data=None,
            processing_status=ProcessingStatusEnum.PROCESSED,
        )

        payment = SimpleNamespace(
            id=payment_id,
            amount=Decimal("150.00"),
            receipt=receipt,
            category=category,
            beneficiary=beneficiary,
            source_institution=source_institution,
            destination_institution=destination_institution,
            created_at=utcnow(),
            payment_date=date(2026, 9, 15),
        )

        payment_service.find_by.return_value = payment
        payment_service.update_payment.return_value = payment
        receipt_service.update_receipt_payment.return_value = receipt

        result = await service.update_payment(payment_id=str(payment_id), payload=payload, user=user)

        payment_service.find_by.assert_awaited_once_with(
            id=str(payment_id),
            user_id=str(user.id),
        )

        payment_service.update_payment.assert_awaited_once_with(
            payment_id=str(payment_id),
            payload={
                "amount": payload.amount,
            },
            user=user,
        )
        receipt_service.update_receipt_payment.assert_awaited_once_with(
            receipt_id=receipt.id,
            payload={
                "payer": payload.payer,
                "paid_amount": payment.amount,
                "payment_date": payment.payment_date,
                "category": payment.category.name,
                "beneficiary": payment.beneficiary.name,
                "source_institution": payment.source_institution.name,
                "destination_institution": payment.destination_institution.name
                if payment.destination_institution
                else None,
            },
            user=user,
        )
        category_service.resolve.assert_not_awaited()
        beneficiary_service.resolve.assert_not_awaited()
        institution_service.resolve.assert_not_awaited()

        assert result is payment

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_payment_date():
        session = AsyncMock()
        receipt_service = AsyncMock()
        category_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            receipt_service=receipt_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            institution_service=institution_service,
            category_service=category_service,
        )

        user = SimpleNamespace(id=uuid4())
        payment_id = uuid4()
        payload = FinanceUpdatePaymentRequestSchema(
            payer=None,
            amount=None,
            beneficiary=None,
            payment_date=date(2026, 9, 15),
            source_institution=None,
            destination_institution=None,
        )

        category = SimpleNamespace(
            id=uuid4(),
            name="New Category",
            created_at=utcnow(),
        )

        beneficiary = SimpleNamespace(
            id=uuid4(),
            name="New Beneficiary",
            created_at=utcnow(),
        )

        source_institution = SimpleNamespace(
            id=uuid4(),
            name="New Source Bank",
            created_at=utcnow(),
        )

        destination_institution = SimpleNamespace(
            id=uuid4(),
            name="New Destination Bank",
            created_at=utcnow(),
        )

        receipt = SimpleNamespace(
            id=uuid4(),
            created_at=utcnow(),
            updated_at=None,
            deleted_at=None,
            file_name="receipt.pdf",
            file_type="application/pdf",
            file_size=1024,
            extracted_data=None,
            processing_status=ProcessingStatusEnum.PROCESSED,
        )

        payment = SimpleNamespace(
            id=payment_id,
            amount=Decimal("150.00"),
            receipt=receipt,
            category=category,
            beneficiary=beneficiary,
            source_institution=source_institution,
            destination_institution=destination_institution,
            created_at=utcnow(),
            payment_date=date(2026, 9, 15),
        )

        payment_service.find_by.return_value = payment
        payment_service.update_payment.return_value = payment
        receipt_service.update_receipt_payment.return_value = receipt

        result = await service.update_payment(payment_id=str(payment_id), payload=payload, user=user)

        payment_service.find_by.assert_awaited_once_with(
            id=str(payment_id),
            user_id=str(user.id),
        )

        payment_service.update_payment.assert_awaited_once_with(
            payment_id=str(payment_id),
            payload={
                "payment_date": payload.payment_date,
            },
            user=user,
        )
        receipt_service.update_receipt_payment.assert_awaited_once_with(
            receipt_id=receipt.id,
            payload={
                "payer": payload.payer,
                "paid_amount": payment.amount,
                "payment_date": payment.payment_date,
                "category": payment.category.name,
                "beneficiary": payment.beneficiary.name,
                "source_institution": payment.source_institution.name,
                "destination_institution": payment.destination_institution.name
                if payment.destination_institution
                else None,
            },
            user=user,
        )
        category_service.resolve.assert_not_awaited()
        beneficiary_service.resolve.assert_not_awaited()
        institution_service.resolve.assert_not_awaited()

        assert result is payment

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_beneficiary():
        session = AsyncMock()
        receipt_service = AsyncMock()
        category_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            category_service=category_service,
            receipt_service=receipt_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            institution_service=institution_service,
        )

        user = SimpleNamespace(id=uuid4())
        payment_id = uuid4()

        beneficiary = SimpleNamespace(
            id=uuid4(),
            name="New Beneficiary",
            created_at=utcnow()
        )

        category = SimpleNamespace(
            id=uuid4(),
            name="New Category",
            created_at=utcnow()
        )

        payment = SimpleNamespace(
            id=payment_id,
            amount=Decimal("100.00"),
            category=category,
            payment_date=date(2026, 9, 15),
            receipt=SimpleNamespace(id=uuid4()),
            beneficiary=beneficiary,
            source_institution=SimpleNamespace(name="Source"),
            destination_institution=SimpleNamespace(name="Destination"),
        )

        payload = FinanceUpdatePaymentRequestSchema(
            beneficiary=beneficiary.name,
        )

        payment_service.find_by.return_value = payment
        payment_service.update_payment.return_value = payment
        beneficiary_service.resolve.return_value = beneficiary

        await service.update_payment(
            payment_id=str(payment_id),
            payload=payload,
            user=user,
        )

        beneficiary_service.resolve.assert_awaited_once_with(
            name=beneficiary.name,
        )

        payment_service.update_payment.assert_awaited_once_with(
            payment_id=str(payment_id),
            payload={
                "beneficiary_id": beneficiary.id,
            },
            user=user,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_source_institution():
        session = AsyncMock()
        category_service = AsyncMock()
        receipt_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            category_service=category_service,
            receipt_service=receipt_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            institution_service=institution_service,
        )

        user = SimpleNamespace(id=uuid4())
        payment_id = str(uuid4())

        institution = SimpleNamespace(
            id=uuid4(),
            name="New Source Bank",
        )

        payment = SimpleNamespace(
            amount=Decimal("100.00"),
            payment_date=date(2026, 9, 15),
            receipt=SimpleNamespace(id=uuid4()),
            beneficiary=SimpleNamespace(name="Beneficiary"),
            category=SimpleNamespace(name="Category"),
            source_institution=institution,
            destination_institution=SimpleNamespace(name="Destination"),
        )

        payload = FinanceUpdatePaymentRequestSchema(
            source_institution=institution.name,
        )

        payment_service.find_by.return_value = payment
        payment_service.update_payment.return_value = payment
        institution_service.resolve.return_value = institution

        await service.update_payment(
            payment_id=payment_id,
            payload=payload,
            user=user,
        )

        institution_service.resolve.assert_awaited_once_with(
            name=institution.name,
        )

        payment_service.update_payment.assert_awaited_once_with(
            payment_id=payment_id,
            payload={
                "source_institution_id": institution.id,
            },
            user=user,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_destination_institution():
        session = AsyncMock()
        category_service = AsyncMock()
        receipt_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            category_service=category_service,
            receipt_service=receipt_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            institution_service=institution_service,
        )

        user = SimpleNamespace(id=uuid4())
        payment_id = str(uuid4())

        institution = SimpleNamespace(
            id=uuid4(),
            name="New Destination Bank",
        )

        payment = SimpleNamespace(
            amount=Decimal("100.00"),
            payment_date=date(2026, 9, 15),
            receipt=SimpleNamespace(id=uuid4()),
            beneficiary=SimpleNamespace(name="Beneficiary"),
            category=SimpleNamespace(name="Category"),
            source_institution=SimpleNamespace(name="Source"),
            destination_institution=institution,
        )

        payload = FinanceUpdatePaymentRequestSchema(
            destination_institution=institution.name,
        )

        payment_service.find_by.return_value = payment
        payment_service.update_payment.return_value = payment
        institution_service.resolve.return_value = institution

        await service.update_payment(
            payment_id=payment_id,
            payload=payload,
            user=user,
        )

        institution_service.resolve.assert_awaited_once_with(
            name=institution.name,
        )

        payment_service.update_payment.assert_awaited_once_with(
            payment_id=payment_id,
            payload={
                "destination_institution_id": institution.id,
            },
            user=user,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_receipt_without_destination_institution():
        session = AsyncMock()
        category_service = AsyncMock()
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
            category_service=category_service,
        )

        user = SimpleNamespace(id=uuid4())
        payment_id = str(uuid4())

        beneficiary = SimpleNamespace(
            id=uuid4(),
            name="Beneficiary",
            created_at=utcnow()
        )

        category = SimpleNamespace(
            id=uuid4(),
            name="Category",
            created_at=utcnow()
        )

        source_institution = SimpleNamespace(
            id=uuid4(),
            name="Source",
            created_at=utcnow()
        )

        payment = SimpleNamespace(
            amount=Decimal("100.00"),
            payment_date=date(2026, 9, 15),
            receipt=SimpleNamespace(id=uuid4()),
            category=category,
            beneficiary=beneficiary,
            source_institution=source_institution,
            destination_institution=None,
        )

        payload = FinanceUpdatePaymentRequestSchema(
            payer="Payer",
            amount=Decimal("100.00"),
            category=category.name,
            beneficiary=beneficiary.name,
            payment_date=date(2026, 9, 15),
            source_institution=source_institution.name,
        )

        payment_service.find_by.return_value = payment
        payment_service.update_payment.return_value = payment

        beneficiary_service.resolve.return_value = beneficiary
        category_service.resolve.return_value = category
        institution_service.resolve.return_value = source_institution

        receipt_service.update_receipt_payment.return_value = payment.receipt

        await service.update_payment(
            payment_id=payment_id,
            payload=payload,
            user=user,
        )

        receipt_service.update_receipt_payment.assert_awaited_once_with(
            user=user,
            receipt_id=payment.receipt.id,
            payload={
                "payer": payload.payer,
                "paid_amount": payment.amount,
                "payment_date": payment.payment_date,
                "category": category.name,
                "beneficiary": beneficiary.name,
                "source_institution": source_institution.name,
                "destination_institution": None,
            },
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_reraises_dependency_error():
        session = AsyncMock()
        receipt_service = AsyncMock()
        category_service = AsyncMock()
        payment_service = AsyncMock()
        beneficiary_service = AsyncMock()
        institution_service = AsyncMock()

        service = FinanceService(
            session=session,
            receipt_service=receipt_service,
            payment_service=payment_service,
            beneficiary_service=beneficiary_service,
            category_service=category_service,
            institution_service=institution_service,
        )

        payment_id = str(uuid4())
        payload = FinanceUpdatePaymentRequestSchema(
            payer="New Payer",
            amount=Decimal("150.00"),
            category="New Category",
            beneficiary="New Beneficiary",
            payment_date=date(2026, 9, 15),
            source_institution="New Source Bank",
            destination_institution="New Destination Bank",
        )

        receipt_service.update_receipt_payment.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            await service.update_payment(
                payment_id=payment_id,
                payload=payload,
                user=SimpleNamespace(id=uuid4()),
            )

        payment_service.create.assert_not_awaited()