from __future__ import annotations

from datetime import date
from decimal import Decimal
from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.domain.finance.payment.schema import (
    PaymentDashboardRequestSchema,
    PaymentDashboardResponseSchema,
    PaymentDashboardPeriodSchema,
    PaymentDashboardSummarySchema,
    PaymentDashboardMonthlySchema,
    PaymentDashboardInstitutionSchema,
    PaymentDashboardBeneficiarySchema, PaymentDashboardCategorySchema, PaymentDashboardPayerSchema,
)
from app.domain.finance.payment.service import PaymentService
from app.models import Payment, utcnow, ProcessingStatusEnum
from app.shared.schemas import FilterPage


@pytest.fixture
def user():
    return SimpleNamespace(
        id=uuid4(),
        username="jorge",
        created_at=utcnow(),
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
        description=None,
        beneficiary=beneficiary,
        source_institution=source_institution,
        destination_institution=destination_institution,
        created_at=utcnow(),
        payment_date=date(2026, 9, 15),
    )


class TestPaymentService:
    @staticmethod
    def test_from_session_builds_service():
        service = PaymentService.from_session(AsyncMock())

        assert isinstance(service, PaymentService)


class TestPaymentServiceCheckReceipt:
    @staticmethod
    @pytest.mark.asyncio
    async def test_check_receipt_does_not_raise_when_payment_does_not_exist(
        user, payment
    ):
        service = PaymentService(AsyncMock())
        service.find_by = AsyncMock(return_value=None)

        receipt_id = payment.receipt.id

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
    async def test_check_receipt_raises_when_payment_already_exists(user, payment):
        service = PaymentService(AsyncMock())
        service.find_by = AsyncMock(return_value=payment)

        receipt_id = payment.receipt.id

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


class TestPaymentServiceCreate:
    @staticmethod
    @pytest.mark.asyncio
    async def test_create_builds_and_saves_payment(user, payment):
        repository = AsyncMock()
        service = PaymentService(repository)

        expected = payment
        repository.save.return_value = expected

        result = await service.create(
            user_id=user.id,
            payer_id=payment.payer.id,
            receipt_id=payment.receipt.id,
            category_id=payment.category.id,
            amount=payment.amount,
            payment_date=payment.payment_date,
            description=payment.description,
            beneficiary_id=payment.beneficiary.id,
            source_institution_id=payment.source_institution.id,
            destination_institution_id=payment.destination_institution.id,
        )

        assert result is expected

        repository.save.assert_awaited_once()

        entity = repository.save.await_args.kwargs["entity"]

        assert isinstance(entity, Payment)
        assert entity.amount == payment.amount
        assert entity.description == payment.description
        assert entity.user_id == user.id
        assert entity.receipt_id == payment.receipt.id
        assert entity.payer_id == payment.payer.id
        assert entity.payment_date == payment.payment_date
        assert entity.beneficiary_id == payment.beneficiary.id
        assert entity.source_institution_id == payment.source_institution.id
        assert entity.destination_institution_id == payment.destination_institution.id
        assert entity.category_id == payment.category.id

    @staticmethod
    @pytest.mark.asyncio
    async def test_create_allows_destination_institution_to_be_none(user, payment):
        repository = AsyncMock()
        service = PaymentService(repository)

        payment.description = None
        payment.destination_institution = None
        payment.destination_institution_id = None
        repository.save.return_value = payment

        await service.create(
            user_id=user.id,
            payer_id=payment.payer.id,
            receipt_id=payment.receipt.id,
            category_id=payment.category.id,
            amount=payment.amount,
            payment_date=payment.payment_date,
            beneficiary_id=payment.beneficiary.id,
            description=None,
            source_institution_id=payment.source_institution.id,
            destination_institution_id=None,
        )

        repository.save.assert_awaited_once()

        entity = repository.save.await_args.kwargs["entity"]

        assert entity.destination_institution_id is None


class TestPaymentServiceList:
    @staticmethod
    @pytest.mark.asyncio
    async def test_list_returns_repository_result(user):
        repository = AsyncMock()
        service = PaymentService(repository)

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
    async def test_list_returns_exception_pagination_when_repository_raises(user):
        repository = AsyncMock()
        service = PaymentService(repository)

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
    async def test_list_returns_exception_pagination_when_repository_raises_without_filter(
        user,
    ):
        repository = AsyncMock()
        service = PaymentService(repository)

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
    async def test_list_logs_success_after_repository_call(user):
        repository = AsyncMock()
        service = PaymentService(repository)

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
    async def test_list_logs_success_even_when_repository_raises(user):
        repository = AsyncMock()
        service = PaymentService(repository)

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


class TestPaymentServiceSummaryCount:
    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_count_returns_repository_result():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        page_filter = FilterPage.build(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        expected = {"count": 2}

        repository.summary_count.return_value = expected

        result = await service.summary_count(
            user=user,
            page_filter=page_filter,
        )

        assert result is expected

        repository.summary_count.assert_awaited_once_with(
            user_id=user.id,
            page_filter=page_filter,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_count_returns_repository_when_repository_raises():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        exception = Exception("Repository error")
        repository.summary_count.side_effect = exception

        with (
            patch("app.domain.finance.payment.service.handle_service_exception"),
        ):
            await service.summary_count(
                user=user,
                page_filter=None,
            )

        repository.summary_count.assert_awaited_once_with(
            user_id=user.id,
            page_filter=None,
        )


class TestPaymentServiceSummaryTotal:
    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_total_returns_repository_result():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        page_filter = FilterPage.build(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        expected = {"total": 2}

        repository.summary_total.return_value = expected

        result = await service.summary_total(
            user=user,
            page_filter=page_filter,
        )

        assert result is expected

        repository.summary_total.assert_awaited_once_with(
            user_id=user.id,
            page_filter=page_filter,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_total_returns_repository_when_repository_raises():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        exception = Exception("Repository error")
        repository.summary_total.side_effect = exception

        with (
            patch("app.domain.finance.payment.service.handle_service_exception"),
        ):
            await service.summary_total(
                user=user,
                page_filter=None,
            )

        repository.summary_total.assert_awaited_once_with(
            user_id=user.id,
            page_filter=None,
        )


class TestPaymentServiceSummaryMax:
    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_max_returns_repository_result(user, payment):
        repository = AsyncMock()
        service = PaymentService(repository)

        page_filter = FilterPage.build(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        repository.summary_order_by.return_value = payment

        result = await service.summary_max(
            user=user,
            page_filter=page_filter,
        )
        assert result.payment.id == payment.id
        assert result.payment.amount == payment.amount
        assert result.payment.payment_date == payment.payment_date
        assert result.payment.description == payment.description
        assert result.payment.created_at == payment.created_at

        assert result.payment.payer.id == payment.payer.id
        assert result.payment.payer.name == payment.payer.name
        assert result.payment.payer.created_at == payment.payer.created_at

        assert result.payment.category.id == payment.category.id
        assert result.payment.category.name == payment.category.name
        assert result.payment.category.created_at == payment.category.created_at

        assert result.payment.beneficiary.id == payment.beneficiary.id
        assert result.payment.beneficiary.name == payment.beneficiary.name
        assert result.payment.beneficiary.created_at == payment.beneficiary.created_at

        assert result.payment.receipt.id == payment.receipt.id
        assert result.payment.receipt.file_name == payment.receipt.file_name
        assert result.payment.receipt.created_at == payment.receipt.created_at

        assert result.payment.source_institution.id == payment.source_institution.id
        assert result.payment.source_institution.name == payment.source_institution.name
        assert (
            result.payment.source_institution.created_at
            == payment.source_institution.created_at
        )

        repository.summary_order_by.assert_awaited_once_with(
            user_id=user.id,
            order_by="desc",
            page_filter=page_filter,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_max_returns_repository_when_repository_raises(user):
        repository = AsyncMock()
        service = PaymentService(repository)

        exception = Exception("Repository error")
        repository.summary_order_by.side_effect = exception

        with (
            patch("app.domain.finance.payment.service.handle_service_exception"),
        ):
            await service.summary_max(
                user=user,
                page_filter=None,
            )

        repository.summary_order_by.assert_awaited_once_with(
            user_id=user.id,
            order_by="desc",
            page_filter=None,
        )


class TestPaymentServiceSummaryMin:
    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_min_returns_repository_result(user, payment):
        repository = AsyncMock()
        service = PaymentService(repository)

        page_filter = FilterPage.build(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        repository.summary_order_by.return_value = payment

        result = await service.summary_min(
            user=user,
            page_filter=page_filter,
        )
        assert result.payment.id == payment.id
        assert result.payment.amount == payment.amount
        assert result.payment.payment_date == payment.payment_date
        assert result.payment.description == payment.description
        assert result.payment.created_at == payment.created_at

        assert result.payment.payer.id == payment.payer.id
        assert result.payment.payer.name == payment.payer.name
        assert result.payment.payer.created_at == payment.payer.created_at

        assert result.payment.category.id == payment.category.id
        assert result.payment.category.name == payment.category.name
        assert result.payment.category.created_at == payment.category.created_at

        assert result.payment.beneficiary.id == payment.beneficiary.id
        assert result.payment.beneficiary.name == payment.beneficiary.name
        assert result.payment.beneficiary.created_at == payment.beneficiary.created_at

        assert result.payment.receipt.id == payment.receipt.id
        assert result.payment.receipt.file_name == payment.receipt.file_name
        assert result.payment.receipt.created_at == payment.receipt.created_at

        assert result.payment.source_institution.id == payment.source_institution.id
        assert result.payment.source_institution.name == payment.source_institution.name
        assert (
            result.payment.source_institution.created_at
            == payment.source_institution.created_at
        )

        repository.summary_order_by.assert_awaited_once_with(
            user_id=user.id,
            order_by="asc",
            page_filter=page_filter,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_min_returns_repository_when_repository_raises(user):
        repository = AsyncMock()
        service = PaymentService(repository)

        exception = Exception("Repository error")
        repository.summary_order_by.side_effect = exception

        with (
            patch("app.domain.finance.payment.service.handle_service_exception"),
        ):
            await service.summary_min(
                user=user,
                page_filter=None,
            )

        repository.summary_order_by.assert_awaited_once_with(
            user_id=user.id,
            order_by="asc",
            page_filter=None,
        )


class TestPaymentServiceSummaryBeneficiary:
    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_beneficiary_returns_raises_when_dont_received_filters():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.summary_beneficiary(
                user=user,
                page_filter=None,
            )
        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert (
            exc_info.value.detail
            == "The beneficiary query parameter is required for the query"
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_beneficiary_returns_raises_when_dont_received_beneficiar_param():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        page_filter = FilterPage.build(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.summary_beneficiary(
                user=user,
                page_filter=page_filter,
            )
        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert (
            exc_info.value.detail
            == "The beneficiary query parameter is required for the query"
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_beneficiary_returns_repository_result():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        page_filter = FilterPage.build(
            beneficiary="Amazon",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        expected = {"beneficiary": "Amazon", "total": Decimal("2000")}

        repository.summary_beneficiary.return_value = expected

        result = await service.summary_beneficiary(
            user=user,
            page_filter=page_filter,
        )

        assert result is expected

        repository.summary_beneficiary.assert_awaited_once_with(
            user_id=user.id,
            beneficiary="Amazon",
            page_filter=page_filter,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_summary_beneficiary_returns_repository_when_repository_raises():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        page_filter = FilterPage.build(
            beneficiary="Amazon",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        exception = Exception("Repository error")
        repository.summary_beneficiary.side_effect = exception

        with (
            patch("app.domain.finance.payment.service.handle_service_exception"),
        ):
            await service.summary_beneficiary(
                user=user,
                page_filter=page_filter,
            )

        repository.summary_beneficiary.assert_awaited_once_with(
            user_id=user.id,
            beneficiary="Amazon",
            page_filter=page_filter,
        )


class TestPaymentServiceUpdatePayment:
    @staticmethod
    @pytest.mark.asyncio
    async def test_update_payment_calls_repository_update():
        repository = AsyncMock()
        service = PaymentService(repository)

        payment_id = uuid4()
        original_updated_at = utcnow()
        payment = SimpleNamespace(
            id=payment_id,
            amount=Decimal("100.00"),
            payment_date=date(2026, 9, 15),
            updated_at=original_updated_at,
        )

        payload: dict[str, object] = {
            "amount": Decimal("150.00"),
            "payment_date": date(2026, 9, 15),
        }

        expected = SimpleNamespace(id=uuid4())
        service.find_by = AsyncMock(return_value=payment)
        repository.save.return_value = expected

        result = await service.update_payment(
            payment_id=str(payment_id),
            payload=payload,
            user=SimpleNamespace(id=uuid4(), username="jorge"),
        )

        assert result is expected
        repository.save.assert_awaited_once()
        assert payment.updated_at is not original_updated_at

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_payment_keeps_updated_at_when_values_are_unchanged():
        repository = AsyncMock()
        service = PaymentService(repository)
        updated_at = utcnow()
        payment = SimpleNamespace(
            amount=Decimal("150.00"),
            payment_date=date(2026, 9, 15),
            updated_at=updated_at,
        )
        service.find_by = AsyncMock(return_value=payment)

        await service.update_payment(
            payment_id=str(uuid4()),
            payload={
                "amount": Decimal("150.00"),
                "payment_date": date(2026, 9, 15),
            },
            user=SimpleNamespace(id=uuid4(), username="jorge"),
        )

        assert payment.updated_at is updated_at

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_payment_ignores_updated_at_from_payload():
        repository = AsyncMock()
        service = PaymentService(repository)
        updated_at = utcnow()
        payment = SimpleNamespace(updated_at=updated_at)
        service.find_by = AsyncMock(return_value=payment)

        await service.update_payment(
            payment_id=str(uuid4()),
            payload={"updated_at": utcnow()},
            user=SimpleNamespace(id=uuid4(), username="jorge"),
        )

        assert payment.updated_at is updated_at

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_payment_raises_when_payment_does_not_exist():
        repository = AsyncMock()
        service = PaymentService(repository)

        payment_id = uuid4()
        user = SimpleNamespace(id=uuid4(), username="testuser")
        payload: dict[str, object] = {
            "amount": Decimal("150.00"),
            "payment_date": date(2026, 9, 15),
        }

        service.find_by = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.update_payment(
                payment_id=str(payment_id),
                payload=payload,
                user=user,
            )
        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == "Payment not found"

        service.find_by.assert_awaited_once_with(
            id=str(payment_id),
            user_id=str(user.id),
            without_throw=True,
        )


class TestPaymentServiceGetDashboard:
    @staticmethod
    @pytest.mark.asyncio
    async def test_get_dashboard_returns_dashboard_response():
        repository = AsyncMock()
        service = PaymentService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        payer_id = uuid4()
        category_id = uuid4()
        beneficiary_id = uuid4()
        institution_id = uuid4()

        params = PaymentDashboardRequestSchema(
            payer_id=payer_id,
            category_id=category_id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 9, 30),
            institution="itau",
            beneficiary_id=beneficiary_id,
        )

        repository.dashboard_summary.return_value = {
            "total": Decimal("5000.00"),
            "count": 10,
            "average": Decimal("500.00"),
            "highest": Decimal("1500.00"),
        }

        repository.dashboard_monthly.return_value = [
            {
                "period": "2026-01",
                "total": Decimal("1000.00"),
                "count": 2,
            },
            {
                "period": "2026-02",
                "total": Decimal("4000.00"),
                "count": 8,
            },
        ]

        repository.dashboard_institutions.return_value = [
            {
                "institution_id": institution_id,
                "institution": "itau",
                "total": Decimal("5000.00"),
                "count": 10,
            },
        ]

        repository.dashboard_beneficiaries.return_value = [
            {
                "beneficiary_id": beneficiary_id,
                "name": "Amazon",
                "total": Decimal("5000.00"),
                "count": 10,
            },
        ]

        repository.dashboard_categories.return_value = [
            {
                "category_id": category_id,
                "name": "Cartão de Crédito",
                "total": Decimal("5000.00"),
                "count": 10,
            },
        ]

        repository.dashboard_payers.return_value = [
            {
                "payer_id": payer_id,
                "name": "John Doe",
                "total": Decimal("5000.00"),
                "count": 10,
            },
        ]

        result = await service.get_dashboard(
            params=params,
            user=user,
        )

        assert isinstance(result, PaymentDashboardResponseSchema)

        assert result.period == PaymentDashboardPeriodSchema(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 9, 30),
        )

        assert result.summary == PaymentDashboardSummarySchema(
            total=Decimal("5000.00"),
            count=10,
            average=Decimal("500.00"),
            highest=Decimal("1500.00"),
        )

        assert result.monthly == [
            PaymentDashboardMonthlySchema(
                period="2026-01",
                total=Decimal("1000.00"),
                count=2,
            ),
            PaymentDashboardMonthlySchema(
                period="2026-02",
                total=Decimal("4000.00"),
                count=8,
            ),
        ]

        assert result.institutions == [
            PaymentDashboardInstitutionSchema(
                institution="itau",
                total=Decimal("5000.00"),
                count=10,
            ),
        ]

        assert result.beneficiaries == [
            PaymentDashboardBeneficiarySchema(
                beneficiary_id=beneficiary_id,
                name="Amazon",
                total=Decimal("5000.00"),
                count=10,
            ),
        ]

        assert result.categories == [
            PaymentDashboardCategorySchema(
                category_id=category_id,
                name="Cartão de Crédito",
                total=Decimal("5000.00"),
                count=10,
            ),
        ]

        assert result.payers == [
            PaymentDashboardPayerSchema(
                payer_id=payer_id,
                name="John Doe",
                total=Decimal("5000.00"),
                count=10,
            ),
        ]

        repository.dashboard_summary.assert_awaited_once_with(
            user_id=user.id,
            end_date=params.end_date,
            start_date=params.start_date,
            institution=params.institution,
            beneficiary_id=params.beneficiary_id,
        )

        repository.dashboard_monthly.assert_awaited_once_with(
            user_id=user.id,
            start_date=params.start_date,
            end_date=params.end_date,
            institution=params.institution,
            beneficiary_id=params.beneficiary_id,
        )

        repository.dashboard_institutions.assert_awaited_once_with(
            user_id=user.id,
            start_date=params.start_date,
            end_date=params.end_date,
            institution=params.institution,
            beneficiary_id=params.beneficiary_id,
        )

        repository.dashboard_beneficiaries.assert_awaited_once_with(
            user_id=user.id,
            start_date=params.start_date,
            end_date=params.end_date,
            institution=params.institution,
            beneficiary_id=params.beneficiary_id,
        )

        repository.dashboard_categories.assert_awaited_once_with(
            user_id=user.id,
            start_date=params.start_date,
            end_date=params.end_date,
            institution=params.institution,
            category_id=params.category_id,
        )

        repository.dashboard_payers.assert_awaited_once_with(
            user_id=user.id,
            start_date=params.start_date,
            end_date=params.end_date,
            institution=params.institution,
            payer_id=params.payer_id,
        )
