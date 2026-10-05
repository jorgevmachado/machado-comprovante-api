from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.finance.category.schema import CategoryPersistSchema
from app.shared.schemas import FilterPage

from app.domain.finance.category.route import (
    list_all,
    category_filter,
    category_service,
    find_one,
    create,
    update,
)
from app.domain.finance.category.service import CategoryService


def test_category_builds_service() -> None:
    service = category_service(AsyncMock())
    assert isinstance(service, CategoryService)


def test_get_category_filter_builds_dynamic_filter():
    page_filter = category_filter(
        page=1,
        name="Category Name",
        limit=12,
        clean_cache=True,
    )

    assert page_filter.page == 1
    assert page_filter.name == "Category Name"
    assert page_filter.limit == 12
    assert page_filter.clean_cache


@pytest.mark.asyncio
async def test_finance_category_route_list_all_paginate_and_filter() -> None:
    service = AsyncMock()
    page_filter = category_filter(page=1, limit=12)
    expected = SimpleNamespace(items=[])
    service.list.return_value = expected
    current_user = SimpleNamespace(id="user-id", username="Finance User")

    result = await list_all(
        current_user=current_user,
        service=service,
        page_filter=page_filter,
    )

    assert result is expected
    service.list.assert_awaited_once()
    called_page_filter = service.list.await_args.kwargs["page_filter"]

    assert (
        called_page_filter.model_dump()
        == FilterPage.build(page_filter=page_filter).model_dump()
    )
    assert service.list.await_args.kwargs["user"] == current_user


@pytest.mark.asyncio
async def test_finance_category_route_find_by_id() -> None:
    service = AsyncMock()
    category_id = uuid4()
    expected = SimpleNamespace(id=category_id, name="Category Name")
    service.find_by.return_value = expected
    current_user = SimpleNamespace(id="user-id", username="Finance User")

    result = await find_one(
        param=str(category_id),
        service=service,
        current_user=current_user,
    )

    assert result is expected
    service.find_by.assert_awaited_once_with(
        id=str(category_id),
        user_id=str(current_user.id),
        user_request=current_user.username
    )

@pytest.mark.asyncio
async def test_finance_category_route_create() -> None:
    service = AsyncMock()
    expected = SimpleNamespace(id=uuid4(), name="New Category")
    service.create.return_value = expected
    current_user = SimpleNamespace(id="user-id", username="Finance User")

    payload = CategoryPersistSchema(name="New Category")

    result = await create(
        service=service,
        payload=payload,
        current_user=current_user,
    )

    assert result is expected
    service.create.assert_awaited_once_with(
        user_id=str(current_user.id),
        name=payload.name,
        description=payload.description
    )

@pytest.mark.asyncio
async def test_finance_category_route_update() -> None:
    service = AsyncMock()
    category_id = uuid4()
    expected = SimpleNamespace(id=category_id, name="New Category")
    service.update.return_value = expected
    current_user = SimpleNamespace(id="user-id", username="Finance User")

    payload = CategoryPersistSchema(name="New Category")

    result = await update(
        service=service,
        payload=payload,
        category_id=str(category_id),
        current_user=current_user,
    )

    assert result is expected
    service.update.assert_awaited_once_with(
        param=str(category_id),
        update_schema=payload,
        user_request=current_user.username
    )