from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.domain.finance.payment.route import (
    list_all,
    payment_filter,
    payment_service,
    summary_count,
    summary_total, summary_max, summary_min,
)
from app.domain.finance.payment.service import PaymentService


def test_payment_builds_service() -> None:
    service = payment_service(AsyncMock())

    assert isinstance(service, PaymentService)


def test_get_payment_filter_builds_dynamic_filter() -> None:
    page_filter = payment_filter(
        page=1,
        limit=12,
        offset=10,
        order_by="payment_date",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 30),
        clean_cache=True,
        institution="Itaú",
        beneficiary="Amazon",
        with_deleted=True,
        source_institution="Itaú",
        destination_institution="Nubank",
    )

    assert page_filter.page == 1
    assert page_filter.limit == 12
    assert page_filter.offset == 10
    assert page_filter.order_by == "payment_date"
    assert page_filter.start_date == date(2026, 9, 1)
    assert page_filter.end_date == date(2026, 9, 30)
    assert page_filter.clean_cache is True
    assert page_filter.institution == "Itaú"
    assert page_filter.beneficiary == "Amazon"
    assert page_filter.with_deleted is True
    assert page_filter.source_institution == "Itaú"
    assert page_filter.destination_institution == "Nubank"


@pytest.mark.asyncio
async def test_payment_route_list_all() -> None:
    service = AsyncMock()
    page_filter = payment_filter(
        page=1,
        limit=12,
        beneficiary="Amazon",
    )

    expected = [
        SimpleNamespace(id="payment-1"),
        SimpleNamespace(id="payment-2"),
    ]

    service.list.return_value = expected

    current_user = SimpleNamespace(
        id="user-id",
        username="Payment User",
    )

    result = await list_all(
        service=service,
        current_user=current_user,
        page_filter=page_filter,
    )

    assert result is expected
    service.list.assert_awaited_once_with(
        page_filter=page_filter,
        user=current_user,
    )


@pytest.mark.asyncio
async def test_payment_route_summary_count() -> None:
    service = AsyncMock()
    page_filter = payment_filter(
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 30),
    )

    expected = SimpleNamespace(
        count=2,
    )

    service.summary_count.return_value = expected

    current_user = SimpleNamespace(
        id="user-id",
        username="Payment User",
    )

    result = await summary_count(
        service=service,
        current_user=current_user,
        page_filter=page_filter,
    )

    assert result is expected
    service.summary_count.assert_awaited_once_with(
        page_filter=page_filter,
        user=current_user,
    )


@pytest.mark.asyncio
async def test_payment_route_summary_total() -> None:
    service = AsyncMock()
    page_filter = payment_filter(
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 30),
    )

    expected = SimpleNamespace(
        total=2000,
    )

    service.summary_total.return_value = expected

    current_user = SimpleNamespace(
        id="user-id",
        username="Payment User",
    )

    result = await summary_total(
        service=service,
        current_user=current_user,
        page_filter=page_filter,
    )

    assert result is expected
    service.summary_total.assert_awaited_once_with(
        page_filter=page_filter,
        user=current_user,
    )

@pytest.mark.asyncio
async def test_payment_route_summary_max() -> None:
    service = AsyncMock()
    page_filter = payment_filter(
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 30),
    )

    expected = SimpleNamespace(id="payment-1"),

    service.summary_max.return_value = expected

    current_user = SimpleNamespace(
        id="user-id",
        username="Payment User",
    )

    result = await summary_max(
        service=service,
        current_user=current_user,
        page_filter=page_filter,
    )

    assert result is expected
    service.summary_max.assert_awaited_once_with(
        page_filter=page_filter,
        user=current_user,
    )

@pytest.mark.asyncio
async def test_payment_route_summary_min() -> None:
    service = AsyncMock()
    page_filter = payment_filter(
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 30),
    )

    expected = SimpleNamespace(id="payment-1"),

    service.summary_min.return_value = expected

    current_user = SimpleNamespace(
        id="user-id",
        username="Payment User",
    )

    result = await summary_min(
        service=service,
        current_user=current_user,
        page_filter=page_filter,
    )

    assert result is expected
    service.summary_min.assert_awaited_once_with(
        page_filter=page_filter,
        user=current_user,
    )
