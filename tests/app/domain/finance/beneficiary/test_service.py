from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.domain.finance.beneficiary.service import BeneficiaryService
from app.models import Beneficiary
from app.shared.schemas import FilterPage


class TestBeneficiaryService:
    @staticmethod
    def test_from_session_builds_service():
        service = BeneficiaryService.from_session(AsyncMock())

        assert isinstance(service, BeneficiaryService)

    @staticmethod
    @pytest.mark.asyncio
    async def test_resolve_returns_existing_beneficiary():
        repository = AsyncMock()
        service = BeneficiaryService(repository)

        beneficiary = SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            name="Empresa Exemplo",
            name_code="empresa_exemplo",
        )

        service.find_by = AsyncMock(return_value=beneficiary)

        with patch(
            "app.domain.finance.beneficiary.service.to_snake_case",
            return_value="empresa_exemplo",
        ) as to_snake_case:
            result = await service.resolve("Empresa Exemplo")

        assert result is beneficiary

        to_snake_case.assert_called_once_with("Empresa Exemplo")

        service.find_by.assert_awaited_once_with(
            name_code="empresa_exemplo",
            without_throw=True,
        )

        repository.save.assert_not_awaited()

    @staticmethod
    @pytest.mark.asyncio
    async def test_resolve_creates_beneficiary_when_not_found():
        repository = AsyncMock()
        service = BeneficiaryService(repository)

        service.find_by = AsyncMock(return_value=None)

        expected = SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            name="Empresa Exemplo",
            name_code="empresa_exemplo",
        )

        repository.save.return_value = expected

        with patch(
            "app.domain.finance.beneficiary.service.to_snake_case",
            return_value="empresa_exemplo",
        ) as to_snake_case:
            result = await service.resolve("Empresa Exemplo")

        assert result is expected

        to_snake_case.assert_called_once_with("Empresa Exemplo")

        service.find_by.assert_awaited_once_with(
            name_code="empresa_exemplo",
            without_throw=True,
        )

        repository.save.assert_awaited_once()

        beneficiary = repository.save.await_args.kwargs["entity"]

        assert isinstance(beneficiary, Beneficiary)
        assert beneficiary.name == "Empresa Exemplo"
        assert beneficiary.name_code == "empresa_exemplo"

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_returns_repository_result():
        repository = AsyncMock()
        service = BeneficiaryService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        page_filter = FilterPage.build(
            name="Amazon",
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
        service = BeneficiaryService(repository)

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
                "app.domain.finance.beneficiary.service.handle_service_exception"
            ) as handle_exception,
            patch(
                "app.domain.finance.beneficiary.service.exception_pagination",
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
        service = BeneficiaryService(repository)

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
            patch("app.domain.finance.beneficiary.service.handle_service_exception"),
            patch(
                "app.domain.finance.beneficiary.service.exception_pagination",
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
        service = BeneficiaryService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        expected = []

        repository.list.return_value = expected

        with patch(
                "app.domain.finance.beneficiary.service.log_service_success"
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
        service = BeneficiaryService(repository)

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
            patch("app.domain.finance.beneficiary.service.handle_service_exception"),
            patch(
                "app.domain.finance.beneficiary.service.exception_pagination",
                return_value=expected,
            ),
            patch(
                "app.domain.finance.beneficiary.service.log_service_success"
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
