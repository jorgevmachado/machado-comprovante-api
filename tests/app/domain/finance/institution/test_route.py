from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.shared.schemas import FilterPage

from app.domain.finance.institution.route import (
    list_all,
    institution_filter,
    institution_service,
)
from app.domain.finance.institution.service import InstitutionService


def test_institution_builds_service() -> None:
    service = institution_service(AsyncMock())
    assert isinstance(service, InstitutionService)


def test_get_institution_filter_builds_dynamic_filter():
    page_filter = institution_filter(
        page=1,
        name="Institution Name",
        limit=12,
        clean_cache=True,
    )

    assert page_filter.page == 1
    assert page_filter.name == "Institution Name"
    assert page_filter.limit == 12
    assert page_filter.clean_cache


@pytest.mark.asyncio
async def test_finance_institution_route_list_all_paginate_and_filter() -> None:
    service = AsyncMock()
    page_filter = institution_filter(page=1, limit=12)
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
