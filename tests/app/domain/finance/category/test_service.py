from __future__ import annotations

from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.domain.finance.category.service import CategoryService
from app.models import Category
from app.shared.schemas import FilterPage

class TestCategoryService:
    @staticmethod
    def test_from_session_builds_service():
        service = CategoryService.from_session(AsyncMock())

        assert isinstance(service, CategoryService)

class TestCategoryServiceResolve:
    @staticmethod
    @pytest.mark.asyncio
    async def test_resolve_returns_existing_category():
        repository = AsyncMock()
        service = CategoryService(repository)
        user_id = uuid4()

        category = SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            name="Categoria Exemplo",
            name_code="categoria_exemplo",
            description="Descrição da categoria exemplo",
        )

        service.find_by = AsyncMock(return_value=category)

        with patch(
                "app.domain.finance.category.service.to_snake_case",
                return_value="categoria_exemplo",
        ) as to_snake_case:
            result = await service.resolve(user_id=user_id, name="Categoria Exemplo")

        assert result is category

        to_snake_case.assert_called_once_with("Categoria Exemplo")

        service.find_by.assert_awaited_once_with(
            user_id=user_id,
            name_code="categoria_exemplo",
            without_throw=True,
        )

        repository.save.assert_not_awaited()

    @staticmethod
    @pytest.mark.asyncio
    async def test_resolve_creates_category_when_not_found():
        repository = AsyncMock()
        service = CategoryService(repository)

        service.find_by = AsyncMock(return_value=None)

        user_id = uuid4()

        expected = SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            name="Categoria Exemplo",
            name_code="categoria_exemplo",
        )

        repository.save.return_value = expected

        with patch(
                "app.domain.finance.category.service.to_snake_case",
                return_value="categoria_exemplo",
        ) as to_snake_case:
            result = await service.resolve(user_id=user_id, name="Categoria Exemplo")

        assert result is expected

        to_snake_case.assert_called_once_with("Categoria Exemplo")

        service.find_by.assert_awaited_once_with(
            user_id=user_id,
            name_code="categoria_exemplo",
            without_throw=True,
        )

        repository.save.assert_awaited_once()

        category = repository.save.await_args.kwargs["entity"]

        assert isinstance(category, Category)
        assert category.name == "Categoria Exemplo"
        assert category.name_code == "categoria_exemplo"

class TestCategoryServiceList:
    @staticmethod
    @pytest.mark.asyncio
    async def test_list_returns_repository_result():
        repository = AsyncMock()
        service = CategoryService(repository)

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
        service = CategoryService(repository)

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
                "app.domain.finance.category.service.handle_service_exception"
            ) as handle_exception,
            patch(
                "app.domain.finance.category.service.exception_pagination",
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
        service = CategoryService(repository)

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
            patch("app.domain.finance.category.service.handle_service_exception"),
            patch(
                "app.domain.finance.category.service.exception_pagination",
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
        service = CategoryService(repository)

        user = SimpleNamespace(
            id=uuid4(),
            username="jorge",
        )

        expected = []

        repository.list.return_value = expected

        with patch(
                "app.domain.finance.category.service.log_service_success"
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
        service = CategoryService(repository)

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
            patch("app.domain.finance.category.service.handle_service_exception"),
            patch(
                "app.domain.finance.category.service.exception_pagination",
                return_value=expected,
            ),
            patch(
                "app.domain.finance.category.service.log_service_success"
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

class TestCategoryServiceCreate:
    @staticmethod
    @pytest.mark.asyncio
    async def test_create_returns_not_existing_category():
        repository = AsyncMock()
        service = CategoryService(repository)
        user_id = uuid4()

        category = SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            name="Categoria Exemplo",
            name_code="categoria_exemplo",
            description="Descrição da categoria exemplo",
        )

        service.find_by = AsyncMock(return_value=None)
        service.repository.save = AsyncMock(return_value=category)

        with patch(
                "app.domain.finance.category.service.to_snake_case",
                return_value=category.name_code,
        ) as to_snake_case:
            result = await service.create(user_id=user_id, name=category.name, name_code=None, description=category.description)

        assert result.name is category.name
        assert result.name_code is category.name_code
        assert result.description is category.description

        to_snake_case.assert_called_once_with(category.name)

        service.find_by.assert_awaited_once_with(
            user_id=user_id,
            name_code=category.name_code,
            without_throw=True,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_creates_category_raises_when_category_exists():
        repository = AsyncMock()
        service = CategoryService(repository)

        category = SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            name="Categoria Exemplo",
            name_code="categoria_exemplo",
            description="Descrição da categoria exemplo",
        )

        service.find_by = AsyncMock(return_value=category)

        user_id = uuid4()

        with patch(
                "app.domain.finance.category.service.to_snake_case",
                return_value="categoria_exemplo",
        ) as to_snake_case:
          with pytest.raises(HTTPException) as exc_info:
            await service.create(user_id=user_id, name=category.name, name_code=None, description=category.description)

          assert exc_info.value.status_code == HTTPStatus.CONFLICT
          assert exc_info.value.detail == "Category already exists"

        to_snake_case.assert_called_once_with(category.name)

        service.find_by.assert_awaited_once_with(
            user_id=user_id,
            name_code="categoria_exemplo",
            without_throw=True,
        )