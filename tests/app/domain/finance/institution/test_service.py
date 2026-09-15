from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.domain.finance.institution.service import InstitutionService
from app.models import Institution


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
