from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.domain.finance.beneficiary.service import BeneficiaryService
from app.models import Beneficiary


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
