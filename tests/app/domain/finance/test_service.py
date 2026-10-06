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
from app.domain.finance.payer.service import PayerService
from app.domain.finance.payment.service import PaymentService
from app.domain.finance.receipt.service import ReceiptService
from app.domain.finance.schema import (
    FinanceConfirmRequestSchema,
    FinanceUpdatePaymentRequestSchema,
)
from app.domain.finance.service import FinanceService
from app.models import utcnow
from app.models.enums import ProcessingStatusEnum


@pytest.fixture
def user():
    return SimpleNamespace(
        id=uuid4(),
    )


@pytest.fixture
def payer():
    return SimpleNamespace(id=uuid4(), name="Pessoa Exemplo", created_at=utcnow())


@pytest.fixture
def category():
    return SimpleNamespace(
        id=uuid4(),
        name="Categoria Exemplo",
        created_at=utcnow(),
    )


@pytest.fixture
def beneficiary():
    return SimpleNamespace(
        id=uuid4(),
        name="Empresa Exemplo",
        created_at=utcnow(),
    )


@pytest.fixture
def receipt():
    return SimpleNamespace(
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


@pytest.fixture
def source_institution():
    return SimpleNamespace(
        id=uuid4(),
        name="Banco Exemplo",
        created_at=utcnow(),
    )


@pytest.fixture
def destination_institution():
    return SimpleNamespace(
        id=uuid4(),
        name="Banco Destino",
        created_at=utcnow(),
    )


@pytest.fixture
def payment(
    payer, receipt, category, beneficiary, source_institution, destination_institution
):
    return SimpleNamespace(
        id=uuid4(),
        payer=payer,
        amount=Decimal("150.00"),
        receipt=receipt,
        category=category,
        beneficiary=beneficiary,
        source_institution=source_institution,
        destination_institution=destination_institution,
        created_at=utcnow(),
        payment_date=date(2026, 9, 15),
    )


@pytest.fixture
def service():
    session = AsyncMock()
    payer_service = AsyncMock()
    receipt_service = AsyncMock()
    category_service = AsyncMock()
    payment_service = AsyncMock()
    beneficiary_service = AsyncMock()
    institution_service = AsyncMock()

    return FinanceService(
        session=session,
        payer_service=payer_service,
        receipt_service=receipt_service,
        category_service=category_service,
        payment_service=payment_service,
        beneficiary_service=beneficiary_service,
        institution_service=institution_service,
    )


def build_confirm_payload() -> FinanceConfirmRequestSchema:
    return FinanceConfirmRequestSchema(
        payer="Empresa Exemplo",
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

        assert isinstance(service.payer_service, PayerService)
        assert isinstance(service.category_service, CategoryService)
        assert isinstance(service.receipt_service, ReceiptService)
        assert isinstance(service.payment_service, PaymentService)
        assert isinstance(service.beneficiary_service, BeneficiaryService)
        assert isinstance(service.institution_service, InstitutionService)


class TestFinanceServiceConfirm:
    @staticmethod
    @pytest.mark.asyncio
    async def test_confirm_creates_payment_and_returns_response(
        user,
        payment,
        service,
    ):

        service.receipt_service.validate_confirm_receipt.return_value = payment.receipt
        service.receipt_service.confirm_receipt.return_value = payment.receipt

        service.category_service.resolve.return_value = payment.category
        service.payer_service.resolve.return_value = payment.payer

        service.beneficiary_service.resolve.return_value = payment.beneficiary

        service.institution_service.resolve.side_effect = [
            payment.source_institution,
            payment.destination_institution,
        ]

        service.payment_service.create.return_value = payment

        payload = build_confirm_payload()

        result = await service.confirm(
            receipt_id=str(payment.receipt.id),
            payload=payload,
            user=user,
        )

        assert result.category.id == payment.category.id
        assert result.category.name == payment.category.name

        assert result.beneficiary.id == payment.beneficiary.id
        assert result.beneficiary.name == payment.beneficiary.name

        assert result.payment.id == payment.id
        assert result.payment.amount == payment.amount
        assert result.payment.payment_date == payment.payment_date

        assert result.source_institution.id == payment.source_institution.id
        assert result.source_institution.name == payment.source_institution.name

        assert result.destination_institution is not None
        assert result.destination_institution.id == payment.destination_institution.id
        assert (
            result.destination_institution.name == payment.destination_institution.name
        )

        service.receipt_service.validate_confirm_receipt.assert_awaited_once_with(
            receipt_id=str(payment.receipt.id),
            user=user,
        )

        service.payment_service.check_receipt.assert_awaited_once_with(
            receipt_id=payment.receipt.id,
            user=user,
        )

        service.beneficiary_service.resolve.assert_awaited_once_with(
            name=payload.beneficiary,
        )

        service.category_service.resolve.assert_awaited_once_with(
            name=payload.category,
            user_id=user.id,
        )

        service.payer_service.resolve.assert_awaited_once_with(
            name=payload.payer,
            user_id=user.id,
        )

        assert service.institution_service.resolve.await_count == 2
        service.institution_service.resolve.assert_any_await(
            name=payload.source_institution,
        )
        service.institution_service.resolve.assert_any_await(
            name=payload.destination_institution,
        )

        service.payment_service.create.assert_awaited_once_with(
            amount=payload.paid_amount,
            user_id=user.id,
            payer_id=payment.payer.id,
            receipt_id=payment.receipt.id,
            category_id=payment.category.id,
            description=None,
            payment_date=payload.payment_date,
            beneficiary_id=payment.beneficiary.id,
            source_institution_id=payment.source_institution.id,
            destination_institution_id=payment.destination_institution.id,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_confirm_does_not_resolve_destination_when_not_provided(
        user,
        service,
        payment,
    ):

        service.receipt_service.validate_confirm_receipt.return_value = payment.receipt
        service.receipt_service.confirm_receipt.return_value = payment.receipt
        service.beneficiary_service.resolve.return_value = payment.beneficiary
        service.category_service.resolve.return_value = payment.category
        service.payer_service.resolve.return_value = payment.payer
        service.institution_service.resolve.return_value = payment.source_institution
        service.payment_service.create.return_value = payment

        payload = FinanceConfirmRequestSchema(
            payer="Empresa Exemplo",
            paid_amount=payment.amount,
            payment_date=payment.payment_date,
            category=payment.category.name,
            beneficiary=payment.beneficiary.name,
            source_institution=payment.source_institution.name,
            destination_institution=None,
        )

        result = await service.confirm(
            receipt_id=str(payment.receipt.id),
            payload=payload,
            user=user,
        )

        assert result.destination_institution is None

        service.institution_service.resolve.assert_awaited_once_with(
            name=payload.source_institution,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_confirm_reraises_dependency_error(user, service):

        service.receipt_service.validate_confirm_receipt.side_effect = RuntimeError(
            "boom"
        )

        with pytest.raises(RuntimeError, match="boom"):
            await service.confirm(
                receipt_id="receipt-id",
                payload=build_confirm_payload(),
                user=user,
            )

        service.payment_service.create.assert_not_awaited()


class TestFinanceServiceUpdatePayment:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_payment_and_receipt_with_all_fields(
        user, service, payment
    ):
        payment_id = payment.id
        payload = FinanceUpdatePaymentRequestSchema(
            payer=payment.payer.name,
            amount=payment.amount,
            category=payment.category.name,
            beneficiary=payment.beneficiary.name,
            payment_date=payment.payment_date,
            source_institution=payment.source_institution.name,
            destination_institution=payment.destination_institution.name,
        )

        service.payment_service.find_by.return_value = SimpleNamespace(id=payment_id)

        service.category_service.resolve.return_value = payment.category

        service.beneficiary_service.resolve.return_value = payment.beneficiary

        service.payer_service.resolve.return_value = payment.payer

        service.institution_service.resolve.side_effect = [
            payment.source_institution,
            payment.destination_institution,
        ]

        service.payment_service.update_payment.return_value = payment

        service.receipt_service.update_receipt_payment.return_value = payment.receipt

        expected_payload = {
            "amount": payload.amount,
            "payer_id": payment.payer.id,
            "payment_date": payload.payment_date,
            "category_id": payment.category.id,
            "beneficiary_id": payment.beneficiary.id,
            "source_institution_id": payment.source_institution.id,
            "destination_institution_id": payment.destination_institution.id,
        }

        result = await service.update_payment(
            payment_id=str(payment_id), payload=payload, user=user
        )

        service.payment_service.find_by.assert_awaited_once_with(
            id=str(payment_id),
            user_id=str(user.id),
        )

        service.category_service.resolve.assert_awaited_once_with(
            user_id=user.id,
            name=payload.category,
        )

        service.beneficiary_service.resolve.assert_awaited_once_with(
            name=payload.beneficiary,
        )

        service.payer_service.resolve.assert_awaited_once_with(
            user_id=user.id,
            name=payload.payer,
        )

        service.institution_service.resolve.assert_has_awaits(
            [
                call(name=payload.source_institution),
                call(name=payload.destination_institution),
            ]
        )

        service.payment_service.update_payment.assert_awaited_once_with(
            payment_id=str(payment_id),
            payload=expected_payload,
            user=user,
        )

        assert result is payment

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_payment_when_there_is_nothing_to_update(
        user, service, payment
    ):
        payment_id = payment.id
        payload = FinanceUpdatePaymentRequestSchema(
            payer=None,
            amount=None,
            category=None,
            beneficiary=None,
            payment_date=None,
            source_institution=None,
            destination_institution=None,
        )

        service.payment_service.find_by.return_value = payment

        result = await service.update_payment(
            payment_id=str(payment_id), payload=payload, user=user
        )

        service.payment_service.find_by.assert_awaited_once_with(
            id=str(payment_id),
            user_id=str(user.id),
        )

        service.payment_service.update_payment.assert_not_awaited()
        service.receipt_service.update_receipt_payment.assert_not_awaited()
        service.category_service.resolve.assert_not_awaited()
        service.payer_service.resolve.assert_not_awaited()
        service.beneficiary_service.resolve.assert_not_awaited()
        service.institution_service.resolve.assert_not_awaited()

        assert result is payment

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_amount(user, service, payment):
        payment_id = payment.id
        payload = FinanceUpdatePaymentRequestSchema(
            payer=None,
            amount=payment.amount,
            beneficiary=None,
            payment_date=None,
            source_institution=None,
            destination_institution=None,
        )

        service.payment_service.find_by.return_value = payment
        service.payment_service.update_payment.return_value = payment
        service.receipt_service.update_receipt_payment.return_value = payment.receipt

        result = await service.update_payment(
            payment_id=str(payment_id), payload=payload, user=user
        )

        service.payment_service.find_by.assert_awaited_once_with(
            id=str(payment_id),
            user_id=str(user.id),
        )

        service.payment_service.update_payment.assert_awaited_once_with(
            payment_id=str(payment_id),
            payload={
                "amount": payload.amount,
            },
            user=user,
        )
        service.receipt_service.update_receipt_payment.assert_awaited_once_with(
            receipt_id=payment.receipt.id,
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
        service.category_service.resolve.assert_not_awaited()
        service.payer_service.resolve.assert_not_awaited()
        service.beneficiary_service.resolve.assert_not_awaited()
        service.institution_service.resolve.assert_not_awaited()

        assert result is payment

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_payment_date(user, service, payment):
        payment_id = payment.id
        payload = FinanceUpdatePaymentRequestSchema(
            payer=None,
            amount=None,
            beneficiary=None,
            payment_date=payment.payment_date,
            source_institution=None,
            destination_institution=None,
        )

        service.payment_service.find_by.return_value = payment
        service.payment_service.update_payment.return_value = payment
        service.receipt_service.update_receipt_payment.return_value = payment.receipt

        result = await service.update_payment(
            payment_id=str(payment_id), payload=payload, user=user
        )

        service.payment_service.find_by.assert_awaited_once_with(
            id=str(payment_id),
            user_id=str(user.id),
        )

        service.payment_service.update_payment.assert_awaited_once_with(
            payment_id=str(payment_id),
            payload={
                "payment_date": payload.payment_date,
            },
            user=user,
        )
        service.receipt_service.update_receipt_payment.assert_awaited_once_with(
            receipt_id=payment.receipt.id,
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
        service.category_service.resolve.assert_not_awaited()
        service.payer_service.resolve.assert_not_awaited()
        service.beneficiary_service.resolve.assert_not_awaited()
        service.institution_service.resolve.assert_not_awaited()

        assert result is payment

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_category(user, service, payment):
        payment_id = payment.id

        payload = FinanceUpdatePaymentRequestSchema(
            category=payment.category.name,
        )

        service.payment_service.find_by.return_value = payment
        service.payment_service.update_payment.return_value = payment
        service.category_service.resolve.return_value = payment.category

        await service.update_payment(
            payment_id=str(payment_id),
            payload=payload,
            user=user,
        )

        service.category_service.resolve.assert_awaited_once_with(
            name=payment.category.name, user_id=user.id
        )

        service.payment_service.update_payment.assert_awaited_once_with(
            payment_id=str(payment_id),
            payload={
                "category_id": payment.category.id,
            },
            user=user,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_payer(user, service, payment):
        payment_id = payment.id

        payload = FinanceUpdatePaymentRequestSchema(
            payer=payment.payer.name,
        )

        service.payment_service.find_by.return_value = payment
        service.payment_service.update_payment.return_value = payment
        service.payer_service.resolve.return_value = payment.payer

        await service.update_payment(
            payment_id=str(payment_id),
            payload=payload,
            user=user,
        )

        service.payer_service.resolve.assert_awaited_once_with(
            name=payment.payer.name, user_id=user.id
        )

        service.payment_service.update_payment.assert_awaited_once_with(
            payment_id=str(payment_id),
            payload={
                "payer_id": payment.payer.id,
            },
            user=user,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_beneficiary(user, service, payment):

        payment_id = payment.id

        payload = FinanceUpdatePaymentRequestSchema(
            beneficiary=payment.beneficiary.name,
        )

        service.payment_service.find_by.return_value = payment
        service.payment_service.update_payment.return_value = payment
        service.beneficiary_service.resolve.return_value = payment.beneficiary

        await service.update_payment(
            payment_id=str(payment_id),
            payload=payload,
            user=user,
        )

        service.beneficiary_service.resolve.assert_awaited_once_with(
            name=payment.beneficiary.name,
        )

        service.payment_service.update_payment.assert_awaited_once_with(
            payment_id=str(payment_id),
            payload={
                "beneficiary_id": payment.beneficiary.id,
            },
            user=user,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_source_institution(user, service, payment):
        payment_id = payment.id

        payload = FinanceUpdatePaymentRequestSchema(
            source_institution=payment.source_institution.name,
        )

        service.payment_service.find_by.return_value = payment
        service.payment_service.update_payment.return_value = payment
        service.institution_service.resolve.return_value = payment.source_institution

        await service.update_payment(
            payment_id=payment_id,
            payload=payload,
            user=user,
        )

        service.institution_service.resolve.assert_awaited_once_with(
            name=payment.source_institution.name,
        )

        service.payment_service.update_payment.assert_awaited_once_with(
            payment_id=payment_id,
            payload={
                "source_institution_id": payment.source_institution.id,
            },
            user=user,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_only_destination_institution(user, service, payment):
        payment_id = payment.id

        payload = FinanceUpdatePaymentRequestSchema(
            destination_institution=payment.destination_institution.name,
        )

        service.payment_service.find_by.return_value = payment
        service.payment_service.update_payment.return_value = payment
        service.institution_service.resolve.return_value = (
            payment.destination_institution
        )

        await service.update_payment(
            payment_id=payment_id,
            payload=payload,
            user=user,
        )

        service.institution_service.resolve.assert_awaited_once_with(
            name=payment.destination_institution.name,
        )

        service.payment_service.update_payment.assert_awaited_once_with(
            payment_id=payment_id,
            payload={
                "destination_institution_id": payment.destination_institution.id,
            },
            user=user,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_update_receipt_without_destination_institution(
        user,
        payment,
        service,
    ):
        payment_id = payment.id

        payment.destination_institution = None

        payload = FinanceUpdatePaymentRequestSchema(
            payer="Payer",
            amount=payment.amount,
            category=payment.category.name,
            beneficiary=payment.beneficiary.name,
            payment_date=payment.payment_date,
            source_institution=payment.source_institution.name,
        )

        service.payment_service.find_by.return_value = payment
        service.payment_service.update_payment.return_value = payment

        service.beneficiary_service.resolve.return_value = payment.beneficiary
        service.category_service.resolve.return_value = payment.category
        service.institution_service.resolve.return_value = payment.source_institution

        service.receipt_service.update_receipt_payment.return_value = payment.receipt

        await service.update_payment(
            payment_id=payment_id,
            payload=payload,
            user=user,
        )

        service.receipt_service.update_receipt_payment.assert_awaited_once_with(
            user=user,
            receipt_id=payment.receipt.id,
            payload={
                "payer": payload.payer,
                "paid_amount": payment.amount,
                "payment_date": payment.payment_date,
                "category": payment.category.name,
                "beneficiary": payment.beneficiary.name,
                "source_institution": payment.source_institution.name,
                "destination_institution": None,
            },
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_reraises_dependency_error(user, service, payment):

        payment_id = payment.id

        payload = FinanceUpdatePaymentRequestSchema(
            payer="Payer",
            amount=payment.amount,
            category=payment.category.name,
            beneficiary=payment.beneficiary.name,
            payment_date=payment.payment_date,
            source_institution=payment.source_institution.name,
        )

        service.receipt_service.update_receipt_payment.side_effect = RuntimeError(
            "boom"
        )

        with pytest.raises(RuntimeError, match="boom"):
            await service.update_payment(
                payment_id=payment_id,
                payload=payload,
                user=user,
            )

        service.payment_service.create.assert_not_awaited()
