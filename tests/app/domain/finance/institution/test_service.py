from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.domain.finance.institution.service import InstitutionService
from app.models import Institution
from app.shared.schemas import FilterPage


class TestInstitutionService:
    @staticmethod
    def test_from_session_builds_service():
        service = InstitutionService.from_session(AsyncMock())

        assert isinstance(service, InstitutionService)

    @staticmethod
    @pytest.mark.asyncio
    async def test_resolve_returns_existing_institution():
        repository = AsyncMock()
        service = InstitutionService(repository)

        institution = SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            name="Itaú",
            name_code="itau",
        )

        service.find_by = AsyncMock(return_value=institution)

        with patch(
            "app.domain.finance.institution.service.to_snake_case",
            return_value="itau",
        ) as to_snake_case:
            result = await service.resolve("Itaú")

        assert result is institution

        to_snake_case.assert_called_once_with("Itaú")

        service.find_by.assert_awaited_once_with(
            name_code="itau",
            without_throw=True,
        )

        repository.save.assert_not_awaited()

    @staticmethod
    @pytest.mark.asyncio
    async def test_resolve_creates_institution_when_not_found():
        repository = AsyncMock()
        service = InstitutionService(repository)

        service.find_by = AsyncMock(return_value=None)

        expected = SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            name="Banco Exemplo",
            name_code="banco_exemplo",
        )

        repository.save.return_value = expected

        with patch(
            "app.domain.finance.institution.service.to_snake_case",
            return_value="banco_exemplo",
        ) as to_snake_case:
            result = await service.resolve("Banco Exemplo")

        assert result is expected

        to_snake_case.assert_called_once_with("Banco Exemplo")

        service.find_by.assert_awaited_once_with(
            name_code="banco_exemplo",
            without_throw=True,
        )

        repository.save.assert_awaited_once()

        institution = repository.save.await_args.kwargs["entity"]

        assert isinstance(institution, Institution)
        assert institution.name == "Banco Exemplo"
        assert institution.name_code == "banco_exemplo"

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_returns_repository_result():
        repository = AsyncMock()
        service = InstitutionService(repository)

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
        service = InstitutionService(repository)

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
                "app.domain.finance.institution.service.handle_service_exception"
            ) as handle_exception,
            patch(
                "app.domain.finance.institution.service.exception_pagination",
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
        service = InstitutionService(repository)

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
            patch("app.domain.finance.institution.service.handle_service_exception"),
            patch(
                "app.domain.finance.institution.service.exception_pagination",
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
        service = InstitutionService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        expected = []

        repository.list.return_value = expected

        with patch(
                "app.domain.finance.institution.service.log_service_success"
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
        service = InstitutionService(repository)

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
            patch("app.domain.finance.institution.service.handle_service_exception"),
            patch(
                "app.domain.finance.institution.service.exception_pagination",
                return_value=expected,
            ),
            patch(
                "app.domain.finance.institution.service.log_service_success"
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
