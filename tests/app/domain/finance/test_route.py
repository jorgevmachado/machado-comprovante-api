from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.domain.finance.route import confirm, finance_service
from app.domain.finance.schema import FinanceConfirmRequestSchema
from app.domain.finance.service import FinanceService


def build_confirm_payload() -> FinanceConfirmRequestSchema:
    return FinanceConfirmRequestSchema(
        paid_amount="387.42",
        payment_date="2026-09-12",
        beneficiary="Empresa Exemplo",
        source_institution="Banco Exemplo",
        destination_institution="Banco Destino",
    )


class TestFinanceRoutes:
    @staticmethod
    def test_finance_service_builds_service():
        service = finance_service(AsyncMock())

        assert isinstance(service, FinanceService)

    @staticmethod
    @pytest.mark.asyncio
    async def test_confirm_route_returns_service_result():
        service = AsyncMock()

        receipt_id = "11111111-1111-1111-1111-111111111111"

        current_user = SimpleNamespace(
            id="22222222-2222-2222-2222-222222222222",
        )

        payload = build_confirm_payload()

        expected = SimpleNamespace(
            id="33333333-3333-3333-3333-333333333333",
        )

        service.confirm.return_value = expected

        result = await confirm(
            receipt_id=receipt_id,
            service=service,
            payload=payload,
            current_user=current_user,
        )

        assert result is expected

        service.confirm.assert_awaited_once_with(
            receipt_id=receipt_id,
            payload=payload,
            user=current_user,
        )
