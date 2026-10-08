from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.finance.beneficiary.schema import BeneficiaryPersistSchema
from app.shared.schemas import FilterPage

from app.domain.finance.beneficiary.route import (
    list_all,
    beneficiary_filter,
    beneficiary_service, update,
)
from app.domain.finance.beneficiary.service import BeneficiaryService


def test_beneficiary_builds_service() -> None:
    service = beneficiary_service(AsyncMock())
    assert isinstance(service, BeneficiaryService)


def test_get_beneficiary_filter_builds_dynamic_filter():
    page_filter = beneficiary_filter(
        page=1,
        name="Beneficiary Name",
        limit=12,
        clean_cache=True,
    )

    assert page_filter.page == 1
    assert page_filter.name == "Beneficiary Name"
    assert page_filter.limit == 12
    assert page_filter.clean_cache


@pytest.mark.asyncio
async def test_finance_beneficiary_route_list_all_paginate_and_filter() -> None:
    service = AsyncMock()
    page_filter = beneficiary_filter(page=1, limit=12)
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
async def test_finance_beneficiary_route_update() -> None:
    service = AsyncMock()
    beneficiary_id = uuid4()
    expected = SimpleNamespace(id=beneficiary_id, name="New Beneficiary")
    service.update.return_value = expected
    current_user = SimpleNamespace(id="user-id", username="Finance User")

    payload = BeneficiaryPersistSchema(name="New Beneficiary")

    result = await update(
        service=service,
        payload=payload,
        beneficiary_id=str(beneficiary_id),
        current_user=current_user,
    )

    assert result is expected
    service.update.assert_awaited_once_with(
        param=str(beneficiary_id),
        update_schema=payload,
        user_request=current_user.username,
    )
