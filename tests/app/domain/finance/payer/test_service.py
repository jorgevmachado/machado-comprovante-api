from __future__ import annotations

from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.domain.finance.payer.service import PayerService
from app.models import Payer, utcnow
from app.shared.schemas import FilterPage

@pytest.fixture
def user():
    return SimpleNamespace(
        id=uuid4(),
        username="user"
    )

@pytest.fixture
def payer():
    return SimpleNamespace(id=uuid4(), name="Pessoa Exemplo", name_code="pessoa_exemplo", created_at=utcnow())

class TestPayerService:
    @staticmethod
    def test_from_session_builds_service():
        service = PayerService.from_session(AsyncMock())

        assert isinstance(service, PayerService)


class TestPayerServiceResolve:
    @staticmethod
    @pytest.mark.asyncio
    async def test_resolve_returns_existing_payer(
            user,
            payer
    ):
        repository = AsyncMock()
        service = PayerService(repository)
        user_id=user.id

        service.find_by = AsyncMock(return_value=payer)

        with patch(
            "app.domain.finance.payer.service.to_snake_case",
            return_value=payer.name_code,
        ) as to_snake_case:
            result = await service.resolve(user_id=user_id, name=payer.name)

        assert result is payer

        to_snake_case.assert_called_once_with(payer.name)

        service.find_by.assert_awaited_once_with(
            user_id=user_id,
            name_code=payer.name_code,
            without_throw=True,
        )

        repository.save.assert_not_awaited()

    @staticmethod
    @pytest.mark.asyncio
    async def test_resolve_creates_payer_when_not_found(
            user,
            payer
    ):
        repository = AsyncMock()
        service = PayerService(repository)

        service.find_by = AsyncMock(return_value=None)

        user_id=user.id

        expected = payer

        repository.save.return_value = expected

        with patch(
            "app.domain.finance.payer.service.to_snake_case",
            return_value=payer.name_code,
        ) as to_snake_case:
            result = await service.resolve(user_id=user_id, name=payer.name)

        assert result is expected

        to_snake_case.assert_called_once_with(payer.name)

        service.find_by.assert_awaited_once_with(
            user_id=user_id,
            name_code=payer.name_code,
            without_throw=True,
        )

        repository.save.assert_awaited_once()

        entity = repository.save.await_args.kwargs["entity"]

        assert isinstance(entity, Payer)
        assert entity.name == "Pessoa Exemplo"
        assert entity.name_code == "pessoa_exemplo"


class TestPayerServiceList:
    @staticmethod
    @pytest.mark.asyncio
    async def test_list_returns_repository_result(
            user
    ):
        repository = AsyncMock()
        service = PayerService(repository)

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
    async def test_list_returns_exception_pagination_when_repository_raises(
            user
    ):
        repository = AsyncMock()
        service = PayerService(repository)

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
                "app.domain.finance.payer.service.handle_service_exception"
            ) as handle_exception,
            patch(
                "app.domain.finance.payer.service.exception_pagination",
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
            user
    ):
        repository = AsyncMock()
        service = PayerService(repository)

        exception = Exception("Repository error")
        repository.list.side_effect = exception

        expected = SimpleNamespace(
            items=[],
            total=0,
        )

        with (
            patch("app.domain.finance.payer.service.handle_service_exception"),
            patch(
                "app.domain.finance.payer.service.exception_pagination",
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
    async def test_list_logs_success_after_repository_call(
            user
    ):
        repository = AsyncMock()
        service = PayerService(repository)

        expected = []

        repository.list.return_value = expected

        with patch(
            "app.domain.finance.payer.service.log_service_success"
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
    async def test_list_logs_success_even_when_repository_raises(
            user
    ):
        repository = AsyncMock()
        service = PayerService(repository)

        exception = Exception("Repository error")
        repository.list.side_effect = exception

        expected = SimpleNamespace(
            items=[],
            total=0,
        )

        with (
            patch("app.domain.finance.payer.service.handle_service_exception"),
            patch(
                "app.domain.finance.payer.service.exception_pagination",
                return_value=expected,
            ),
            patch(
                "app.domain.finance.payer.service.log_service_success"
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


class TestPayerServiceCreate:
    @staticmethod
    @pytest.mark.asyncio
    async def test_create_returns_not_existing_payer(
            user,
            payer
    ):
        repository = AsyncMock()
        service = PayerService(repository)
        user_id=user.id

        service.find_by = AsyncMock(return_value=None)
        service.repository.save = AsyncMock(return_value=payer)

        with patch(
            "app.domain.finance.payer.service.to_snake_case",
            return_value=payer.name_code,
        ) as to_snake_case:
            result = await service.create(
                user_id=user_id,
                name=payer.name,
                name_code=None
            )

        assert result.name is payer.name
        assert result.name_code is payer.name_code

        to_snake_case.assert_called_once_with(payer.name)

        service.find_by.assert_awaited_once_with(
            user_id=user_id,
            name_code=payer.name_code,
            without_throw=True,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_creates_payer_raises_when_payer_exists(
            user,
            payer
    ):
        repository = AsyncMock()
        service = PayerService(repository)

        service.find_by = AsyncMock(return_value=payer)

        user_id=user.id

        with patch(
            "app.domain.finance.payer.service.to_snake_case",
            return_value=payer.name_code,
        ) as to_snake_case:
            with pytest.raises(HTTPException) as exc_info:
                await service.create(
                    user_id=user_id,
                    name=payer.name,
                    name_code=None
                )

            assert exc_info.value.status_code == HTTPStatus.CONFLICT
            assert exc_info.value.detail == "Payer already exists"

        to_snake_case.assert_called_once_with(payer.name)

        service.find_by.assert_awaited_once_with(
            user_id=user_id,
            name_code=payer.name_code,
            without_throw=True,
        )
