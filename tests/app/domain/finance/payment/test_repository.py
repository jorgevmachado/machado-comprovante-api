from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from datetime import date
from uuid import uuid4

from sqlalchemy import select

from app.domain.finance.payment.repository import PaymentRepository
from app.models import Payment
from app.shared.schemas import FilterPage


class TestPaymentRepositoryBuildFilter:
    def test_should_filter_by_user_id(self):
        user_id = uuid4()

        query = select(Payment)

        result = PaymentRepository._build_filter(
            query,
            user_id,
        )

        compiled = result.compile()

        assert user_id in compiled.params.values()

    def test_should_filter_by_beneficiary(self):
        user_id = uuid4()
        page_filter = FilterPage.build(
            beneficiary="Amazon",
        )

        query = select(Payment)

        result = PaymentRepository._build_filter(
            query,
            user_id,
            page_filter,
        )

        compiled = result.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        assert "JOIN beneficiaries" in sql
        assert "beneficiaries.name_code = 'amazon'" in sql

    def test_should_filter_by_source_institution(self):
        user_id = uuid4()
        page_filter = FilterPage.build(
            source_institution="Itaú Unibanco",
        )

        query = select(Payment)

        result = PaymentRepository._build_filter(
            query,
            user_id,
            page_filter,
        )

        compiled = result.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        assert "JOIN institutions" in sql
        assert "institutions.name_code = 'itau_unibanco'" in sql

    def test_should_filter_by_destination_institution(self):
        user_id = uuid4()
        page_filter = FilterPage.build(
            destination_institution="Nubank",
        )

        query = select(Payment)

        result = PaymentRepository._build_filter(
            query,
            user_id,
            page_filter,
        )

        compiled = result.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        assert "JOIN institutions" in sql
        assert "institutions.name_code = 'nubank'" in sql

    def test_should_filter_by_start_date(self):
        user_id = uuid4()
        page_filter = FilterPage.build(
            start_date=date(2026, 9, 1),
        )

        query = select(Payment)

        result = PaymentRepository._build_filter(
            query,
            user_id,
            page_filter,
        )

        compiled = result.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        assert "payments.payment_date >= '2026-09-01'" in sql

    def test_should_filter_by_end_date(self):
        user_id = uuid4()
        page_filter = FilterPage.build(
            end_date=date(2026, 9, 30),
        )

        query = select(Payment)

        result = PaymentRepository._build_filter(
            query,
            user_id,
            page_filter,
        )

        compiled = result.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        assert "payments.payment_date <= '2026-09-30'" in sql

    def test_should_filter_by_date_range(self):
        user_id = uuid4()
        page_filter = FilterPage.build(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        query = select(Payment)

        result = PaymentRepository._build_filter(
            query,
            user_id,
            page_filter,
        )

        compiled = result.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        assert "payments.payment_date >= '2026-09-01'" in sql
        assert "payments.payment_date <= '2026-09-30'" in sql

    def test_should_apply_all_filters(self):
        user_id = uuid4()
        page_filter = FilterPage.build(
            beneficiary="Amazon",
            source_institution="Itaú",
            destination_institution="Nubank",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        query = select(Payment)

        result = PaymentRepository._build_filter(
            query,
            user_id,
            page_filter,
        )

        compiled = result.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        assert f"payments.user_id = '{user_id.hex}'" in sql

        assert "JOIN beneficiaries" in sql
        assert "beneficiaries.name_code = 'amazon'" in sql

        assert "JOIN institutions" in sql
        assert "institutions.name_code = 'itau'" in sql
        assert "institutions.name_code = 'nubank'" in sql

        assert "payments.payment_date >= '2026-09-01'" in sql
        assert "payments.payment_date <= '2026-09-30'" in sql

    def test_should_not_add_optional_filters_when_not_provided(self):
        user_id = uuid4()
        page_filter = FilterPage()

        query = select(Payment)

        result = PaymentRepository._build_filter(
            query,
            user_id,
            page_filter,
        )

        compiled = result.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        assert f"payments.user_id = '{user_id.hex}'" in sql
        assert "JOIN beneficiaries" not in sql
        assert "JOIN institutions" not in sql
        assert "payment_date >=" not in sql
        assert "payment_date <=" not in sql

    def test_should_return_query_with_user_filter_when_page_filter_is_none(self):
        user_id = uuid4()

        query = select(Payment)

        result = PaymentRepository._build_filter(
            query,
            user_id,
            None,
        )

        compiled = result.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        assert f"payments.user_id = '{user_id.hex}'" in sql
        assert "JOIN beneficiaries" not in sql
        assert "JOIN institutions" not in sql


class TestPaymentRepositoryList:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_list_payments_without_pagination():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()
        page_filter = FilterPage()

        payment_one = SimpleNamespace(id=uuid4())
        payment_two = SimpleNamespace(id=uuid4())

        expected = [
            payment_one,
            payment_two,
        ]

        scalars_result = MagicMock()
        scalars_result.all.return_value = expected
        session.scalars.return_value = scalars_result

        with (
            patch.object(
                repository,
                "_build_filter",
                side_effect=lambda query, user_id, page_filter: query,
            ) as build_filter,
            patch.object(
                repository,
                "_apply_order_by",
                side_effect=lambda query, page_filter: query,
            ) as apply_order_by,
            patch(
                "app.domain.finance.payment.repository.is_paginate",
                return_value=False,
            ),
        ):
            result = await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        assert result == expected

        build_filter.assert_called_once()
        apply_order_by.assert_called_once()

        session.scalars.assert_awaited_once()
        scalars_result.all.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_list_payments_without_page_filter():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()

        expected = [
            SimpleNamespace(id=uuid4()),
        ]

        scalars_result = MagicMock()
        scalars_result.all.return_value = expected
        session.scalars.return_value = scalars_result

        with (
            patch.object(
                repository,
                "_build_filter",
                side_effect=lambda query, user_id, page_filter: query,
            ) as build_filter,
            patch.object(
                repository,
                "_apply_order_by",
                side_effect=lambda query, page_filter: query,
            ) as apply_order_by,
            patch(
                "app.domain.finance.payment.repository.is_paginate",
                return_value=False,
            ),
        ):
            result = await repository.list(
                user_id=user_id,
                page_filter=None,
            )

        assert result == expected

        build_filter.assert_called_once()

        apply_order_by.assert_called_once_with(
            build_filter.call_args.args[0],
            None,
        )

        session.scalars.assert_awaited_once()
        scalars_result.all.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_apply_filter_and_order_before_executing_query():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()
        page_filter = FilterPage.build(
            beneficiary="Amazon",
        )

        filtered_query = MagicMock()
        ordered_query = MagicMock()

        with (
            patch.object(
                repository,
                "_build_filter",
                return_value=filtered_query,
            ) as build_filter,
            patch.object(
                repository,
                "_apply_order_by",
                return_value=ordered_query,
            ) as apply_order_by,
            patch(
                "app.domain.finance.payment.repository.is_paginate",
                return_value=False,
            ),
        ):
            scalars_result = MagicMock()
            scalars_result.all.return_value = []

            session.scalars.return_value = scalars_result

            result = await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        assert result == []

        build_filter.assert_called_once()

        build_filter_args = build_filter.call_args.args

        assert build_filter_args[1] == user_id
        assert build_filter_args[2] is page_filter

        apply_order_by.assert_called_once_with(
            filtered_query,
            page_filter,
        )

        session.scalars.assert_awaited_once_with(
            ordered_query,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_use_pagination_when_filter_requires_pagination():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()
        page_filter = FilterPage.build(
            page=1,
            limit=10,
        )

        expected = MagicMock()

        with (
            patch.object(
                repository,
                "_build_filter",
                side_effect=lambda query, user_id, page_filter: query,
            ) as build_filter,
            patch.object(
                repository,
                "_apply_order_by",
                side_effect=lambda query, page_filter: query,
            ) as apply_order_by,
            patch.object(
                repository,
                "list_paginate",
                new_callable=AsyncMock,
                return_value=expected,
            ) as list_paginate,
            patch(
                "app.domain.finance.payment.repository.is_paginate",
                return_value=True,
            ) as is_paginate,
        ):
            result = await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        assert result is expected

        is_paginate.assert_called_once_with(page_filter)

        build_filter.assert_called_once()
        apply_order_by.assert_called_once()

        list_paginate.assert_awaited_once()

        session.scalars.assert_not_awaited()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_not_use_pagination_when_page_filter_is_none():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()

        scalars_result = MagicMock()
        scalars_result.all.return_value = []

        session.scalars.return_value = scalars_result

        with (
            patch.object(
                repository,
                "_build_filter",
                side_effect=lambda query, user_id, page_filter: query,
            ),
            patch.object(
                repository,
                "_apply_order_by",
                side_effect=lambda query, page_filter: query,
            ),
            patch.object(
                repository,
                "list_paginate",
                new_callable=AsyncMock,
            ) as list_paginate,
            patch(
                "app.domain.finance.payment.repository.is_paginate",
                return_value=False,
            ),
        ):
            result = await repository.list(
                user_id=user_id,
                page_filter=None,
            )

        assert result == []

        list_paginate.assert_not_awaited()
        session.scalars.assert_awaited_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_all_scalars():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()

        payment_one = SimpleNamespace(id=uuid4())
        payment_two = SimpleNamespace(id=uuid4())
        payment_three = SimpleNamespace(id=uuid4())

        expected = [
            payment_one,
            payment_two,
            payment_three,
        ]

        scalars_result = MagicMock()
        scalars_result.all.return_value = expected
        session.scalars.return_value = scalars_result

        with patch(
            "app.domain.finance.payment.repository.is_paginate",
            return_value=False,
        ):
            result = await repository.list(
                user_id=user_id,
                page_filter=None,
            )

        assert result is expected

        scalars_result.all.assert_called_once_with()
