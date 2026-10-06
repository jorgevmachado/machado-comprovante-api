from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.finance.payer.schema import PayerPersistSchema
from app.shared.schemas import FilterPage

from app.domain.finance.payer.route import (
    list_all,
    payer_filter,
    payer_service,
    find_one,
    create,
    update,
)
from app.domain.finance.payer.service import PayerService


def test_payer_builds_service() -> None:
    service = payer_service(AsyncMock())
    assert isinstance(service, PayerService)


def test_get_payer_filter_builds_dynamic_filter():
    page_filter = payer_filter(
        page=1,
        name="Payer Name",
        limit=12,
        clean_cache=True,
    )

    assert page_filter.page == 1
    assert page_filter.name == "Payer Name"
    assert page_filter.limit == 12
    assert page_filter.clean_cache


@pytest.mark.asyncio
async def test_finance_payer_route_list_all_paginate_and_filter() -> None:
    service = AsyncMock()
    page_filter = payer_filter(page=1, limit=12)
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
async def test_finance_payer_route_find_by_id() -> None:
    service = AsyncMock()
    payer_id = uuid4()
    expected = SimpleNamespace(id=payer_id, name="Payer Name")
    service.find_by.return_value = expected
    current_user = SimpleNamespace(id="user-id", username="Finance User")

    result = await find_one(
        param=str(payer_id),
        service=service,
        current_user=current_user,
    )

    assert result is expected
    service.find_by.assert_awaited_once_with(
        id=str(payer_id),
        user_id=str(current_user.id),
        user_request=current_user.username,
    )


@pytest.mark.asyncio
async def test_finance_payer_route_create() -> None:
    service = AsyncMock()
    expected = SimpleNamespace(id=uuid4(), name="New Payer")
    service.create.return_value = expected
    current_user = SimpleNamespace(id="user-id", username="Finance User")

    payload = PayerPersistSchema(name="New Payer")

    result = await create(
        service=service,
        payload=payload,
        current_user=current_user,
    )

    assert result is expected
    service.create.assert_awaited_once_with(
        user_id=str(current_user.id), name=payload.name
    )


@pytest.mark.asyncio
async def test_finance_payer_route_update() -> None:
    service = AsyncMock()
    payer_id = uuid4()
    expected = SimpleNamespace(id=payer_id, name="New Payer")
    service.update.return_value = expected
    current_user = SimpleNamespace(id="user-id", username="Finance User")

    payload = PayerPersistSchema(name="New Payer")

    result = await update(
        service=service,
        payload=payload,
        payer_id=str(payer_id),
        current_user=current_user,
    )

    assert result is expected
    service.update.assert_awaited_once_with(
        param=str(payer_id),
        update_schema=payload,
        user_request=current_user.username,
    )
