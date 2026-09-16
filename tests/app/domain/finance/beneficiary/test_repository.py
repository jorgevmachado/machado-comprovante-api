from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.domain.finance.beneficiary.repository import BeneficiaryRepository
from app.shared.schemas import FilterPage


class TestBeneficiaryRepositoryList:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_list_beneficiaries_by_user_without_pagination():
        session = AsyncMock()
        repository = BeneficiaryRepository(session)

        user_id = uuid4()

        beneficiary_one = SimpleNamespace(id=uuid4())
        beneficiary_two = SimpleNamespace(id=uuid4())

        expected = [beneficiary_one, beneficiary_two]

        scalars_result = MagicMock()
        scalars_result.all.return_value = expected
        session.scalars.return_value = scalars_result

        with patch(
            "app.domain.finance.beneficiary.repository.is_paginate",
            return_value=False,
        ) as is_paginate:
            result = await repository.list(
                user_id=user_id,
                page_filter=FilterPage(),
            )

        assert result is expected
        is_paginate.assert_called_once_with(FilterPage())
        session.scalars.assert_awaited_once()
        scalars_result.all.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_list_beneficiaries_without_page_filter():
        session = AsyncMock()
        repository = BeneficiaryRepository(session)

        user_id = uuid4()

        beneficiary = SimpleNamespace(id=uuid4())
        expected = [beneficiary]

        scalars_result = MagicMock()
        scalars_result.all.return_value = expected
        session.scalars.return_value = scalars_result

        with patch(
            "app.domain.finance.beneficiary.repository.is_paginate",
            return_value=False,
        ) as is_paginate:
            result = await repository.list(
                user_id=user_id,
                page_filter=None,
            )

        assert result is expected
        is_paginate.assert_not_called()
        session.scalars.assert_awaited_once()
        scalars_result.all.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_apply_name_filter_when_paginating():
        session = AsyncMock()
        repository = BeneficiaryRepository(session)

        user_id = uuid4()
        page_filter = FilterPage.build(
            page=1,
            limit=12,
            name="Amazon",
        )

        expected = MagicMock()

        with patch(
            "app.domain.finance.beneficiary.repository.is_paginate",
            return_value=True,
        ) as is_paginate, patch.object(
            repository,
            "list_paginate",
            new_callable=AsyncMock,
            return_value=expected,
        ) as list_paginate:
            result = await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        assert result is expected
        is_paginate.assert_called_once_with(page_filter)
        list_paginate.assert_awaited_once()

        query = list_paginate.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert "beneficiaries.name_code = 'amazon'" in sql

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_use_pagination_when_filter_requires_pagination():
        session = AsyncMock()
        repository = BeneficiaryRepository(session)

        user_id = uuid4()
        page_filter = FilterPage.build(
            page=1,
            limit=12,
        )

        expected = MagicMock()

        with patch(
            "app.domain.finance.beneficiary.repository.is_paginate",
            return_value=True,
        ) as is_paginate, patch.object(
            repository,
            "list_paginate",
            new_callable=AsyncMock,
            return_value=expected,
        ) as list_paginate:
            result = await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        assert result is expected
        is_paginate.assert_called_once_with(page_filter)
        list_paginate.assert_awaited_once_with(
            list_paginate.await_args.args[0],
            page_filter,
        )
        session.scalars.assert_not_awaited()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_not_use_pagination_when_filter_does_not_require_pagination():
        session = AsyncMock()
        repository = BeneficiaryRepository(session)

        user_id = uuid4()
        page_filter = FilterPage()

        scalars_result = MagicMock()
        scalars_result.all.return_value = []
        session.scalars.return_value = scalars_result

        with patch(
            "app.domain.finance.beneficiary.repository.is_paginate",
            return_value=False,
        ), patch.object(
            repository,
            "list_paginate",
            new_callable=AsyncMock,
        ) as list_paginate:
            result = await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        assert result == []
        list_paginate.assert_not_awaited()
        session.scalars.assert_awaited_once()
        scalars_result.all.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_join_payments_and_use_distinct():
        session = AsyncMock()
        repository = BeneficiaryRepository(session)

        user_id = uuid4()

        scalars_result = MagicMock()
        scalars_result.all.return_value = []
        session.scalars.return_value = scalars_result

        with patch(
            "app.domain.finance.beneficiary.repository.is_paginate",
            return_value=False,
        ):
            await repository.list(
                user_id=user_id,
                page_filter=None,
            )

        query = session.scalars.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert "JOIN payments" in sql
        assert "SELECT DISTINCT" in sql

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_not_apply_name_filter_when_name_is_not_provided():
        session = AsyncMock()
        repository = BeneficiaryRepository(session)

        user_id = uuid4()
        page_filter = FilterPage.build(
            page=1,
            limit=12,
        )

        expected = MagicMock()

        with patch(
                "app.domain.finance.beneficiary.repository.is_paginate",
                return_value=True,
        ), patch.object(
            repository,
            "list_paginate",
            new_callable=AsyncMock,
            return_value=expected,
        ) as list_paginate:
            result = await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        assert result is expected
        list_paginate.assert_awaited_once()

        query = list_paginate.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert "beneficiaries.name_code =" not in sql

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_filter_by_user_id():
        session = AsyncMock()
        repository = BeneficiaryRepository(session)

        user_id = uuid4()

        with patch(
                "app.domain.finance.beneficiary.repository.is_paginate",
                return_value=False,
        ):
            await repository.list(
                user_id=user_id,
                page_filter=FilterPage(),
            )

        query = session.scalars.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert f"payments.user_id = '{user_id.hex}'" in sql