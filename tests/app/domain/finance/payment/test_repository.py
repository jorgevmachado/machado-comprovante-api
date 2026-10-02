from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch, ANY
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
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)

        result = repository._build_filter(
            query,
            user_id,
        )

        compiled = result.compile()

        assert user_id in compiled.params.values()

    def test_should_filter_by_beneficiary(self):
        user_id = uuid4()
        session = AsyncMock()
        repository = PaymentRepository(session)
        page_filter = FilterPage.build(
            beneficiary="Amazon",
        )

        query = select(Payment)

        result = repository._build_filter(
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
        session = AsyncMock()
        repository = PaymentRepository(session)
        page_filter = FilterPage.build(
            source_institution="Itaú Unibanco",
        )

        query = select(Payment)

        result = repository._build_filter(
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
        session = AsyncMock()
        repository = PaymentRepository(session)
        page_filter = FilterPage.build(
            destination_institution="Nubank",
        )

        query = select(Payment)

        result = repository._build_filter(
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
        session = AsyncMock()
        repository = PaymentRepository(session)
        page_filter = FilterPage.build(
            start_date=date(2026, 9, 1),
        )

        query = select(Payment)

        result = repository._build_filter(
            query,
            user_id,
            page_filter,
        )

        compiled = result.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        assert "payments.payment_date >= '2026-09-01'" in sql

    def test_should_filter_by_end_date(self):
        user_id = uuid4()
        session = AsyncMock()
        repository = PaymentRepository(session)
        page_filter = FilterPage.build(
            end_date=date(2026, 9, 30),
        )

        query = select(Payment)

        result = repository._build_filter(
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
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)

        result = repository._build_filter(
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
        session = AsyncMock()
        repository = PaymentRepository(session)
        page_filter = FilterPage.build(
            beneficiary="Amazon",
            source_institution="Itaú",
            destination_institution="Nubank",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        query = select(Payment)

        result = repository._build_filter(
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
        session = AsyncMock()
        repository = PaymentRepository(session)
        page_filter = FilterPage()

        query = select(Payment)

        result = repository._build_filter(
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
        session = AsyncMock()
        repository = PaymentRepository(session)
        query = select(Payment)

        result = repository._build_filter(
            query,
            user_id,
            None,
        )

        compiled = result.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        assert f"payments.user_id = '{user_id.hex}'" in sql
        assert "JOIN beneficiaries" not in sql
        assert "JOIN institutions" not in sql


class TestPaymentRepositoryOnlyFilterDate:
    def test_should_return_page_filter_with_only_date_filters(self):
        page_filter = FilterPage.build(
            beneficiary="Amazon",
            source_institution="Itaú",
            destination_institution="Nubank",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        result = PaymentRepository._only_filter_date(page_filter)

        assert result.start_date == date(2026, 9, 1)
        assert result.end_date == date(2026, 9, 30)
        assert result != page_filter

    def test_should_return_none_when_page_filter_is_none(self):
        result = PaymentRepository._only_filter_date(None)

        assert result is None


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
                "_order_by",
                side_effect=lambda query, page_filter: query,
            ) as _order_by,
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
        _order_by.assert_called_once()

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
                "_order_by",
                side_effect=lambda query, page_filter: query,
            ) as _order_by,
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

        _order_by.assert_called_once_with(
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
                "_order_by",
                return_value=ordered_query,
            ) as _order_by,
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

        _order_by.assert_called_once_with(
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


class TestPaymentRepositorySummaryCount:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_count_of_payments_when_page_filter_is_none():
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
        ):
            result = await repository.summary_count(
                user_id=user_id,
                page_filter=None,
            )

        assert result == {"count": len(expected)}

        build_filter.assert_called_once()

        session.scalars.assert_awaited_once()
        scalars_result.all.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_count_of_payments_when_page_filter_is_not_none():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()
        page_filter = FilterPage(
            beneficiary="Amazon",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        expected_page_filter = FilterPage(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )
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
        ):
            result = await repository.summary_count(
                user_id=user_id,
                page_filter=page_filter,
            )

        assert result == {"count": len(expected)}

        build_filter.assert_called_once_with(ANY, user_id, expected_page_filter)

        session.scalars.assert_awaited_once()
        scalars_result.all.assert_called_once_with()


class TestPaymentRepositorySummaryTotal:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_total_of_payments_when_page_filter_is_none():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()

        list = [
            SimpleNamespace(id=uuid4(), amount=Decimal("4741.75")),
            SimpleNamespace(id=uuid4(), amount=Decimal("132.98")),
        ]

        expected = sum([item.amount for item in list])

        scalars_result = MagicMock()
        scalars_result.all.return_value = list
        session.scalars.return_value = scalars_result

        with (
            patch.object(
                repository,
                "_build_filter",
                side_effect=lambda query, user_id, page_filter: query,
            ) as build_filter,
        ):
            result = await repository.summary_total(
                user_id=user_id,
                page_filter=None,
            )

        assert result == {"total": expected}

        build_filter.assert_called_once()

        session.scalars.assert_awaited_once()
        scalars_result.all.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_total_of_payments_when_page_filter_is_not_none():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()
        page_filter = FilterPage(
            beneficiary="Amazon",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        expected_page_filter = FilterPage(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )
        list = [
            SimpleNamespace(id=uuid4(), amount=Decimal("4741.75")),
        ]
        expected = sum([item.amount for item in list])

        scalars_result = MagicMock()
        scalars_result.all.return_value = list
        session.scalars.return_value = scalars_result

        with (
            patch.object(
                repository,
                "_build_filter",
                side_effect=lambda query, user_id, page_filter: query,
            ) as build_filter,
        ):
            result = await repository.summary_total(
                user_id=user_id,
                page_filter=page_filter,
            )

        assert result == {"total": expected}

        build_filter.assert_called_once_with(ANY, user_id, expected_page_filter)

        session.scalars.assert_awaited_once()
        scalars_result.all.assert_called_once_with()


class TestPaymentRepositorySummaryOrderBy:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_first_payment_when_order_by_is_asc():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()
        page_filter = FilterPage.build(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        expected = SimpleNamespace(
            id=uuid4(),
            amount=Decimal("100.00"),
        )

        scalars_result = MagicMock()
        scalars_result.first.return_value = expected
        session.scalars.return_value = scalars_result

        filtered_query = MagicMock()

        with (
            patch.object(
                repository,
                "_only_filter_date",
                return_value=page_filter,
            ) as only_filter_date,
            patch.object(
                repository,
                "_build_filter",
                return_value=filtered_query,
            ) as build_filter,
        ):
            result = await repository.summary_order_by(
                user_id=user_id,
                order_by="asc",
                page_filter=page_filter,
            )

        assert result is expected

        only_filter_date.assert_called_once_with(page_filter)

        build_filter.assert_called_once_with(
            ANY,
            user_id,
            page_filter,
        )

        session.scalars.assert_awaited_once()
        scalars_result.first.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_first_payment_when_order_by_is_desc():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()
        page_filter = FilterPage.build(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        expected = SimpleNamespace(
            id=uuid4(),
            amount=Decimal("5000.00"),
        )

        scalars_result = MagicMock()
        scalars_result.first.return_value = expected
        session.scalars.return_value = scalars_result

        filtered_query = MagicMock()

        with (
            patch.object(
                repository,
                "_only_filter_date",
                return_value=page_filter,
            ) as only_filter_date,
            patch.object(
                repository,
                "_build_filter",
                return_value=filtered_query,
            ) as build_filter,
        ):
            result = await repository.summary_order_by(
                user_id=user_id,
                order_by="desc",
                page_filter=page_filter,
            )

        assert result is expected

        only_filter_date.assert_called_once_with(page_filter)

        build_filter.assert_called_once_with(
            ANY,
            user_id,
            page_filter,
        )

        session.scalars.assert_awaited_once()
        scalars_result.first.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_use_desc_when_order_by_is_not_asc():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()

        scalars_result = MagicMock()
        scalars_result.first.return_value = None
        session.scalars.return_value = scalars_result

        with (
            patch.object(
                repository,
                "_only_filter_date",
                return_value=None,
            ) as only_filter_date,
            patch.object(
                repository,
                "_build_filter",
                side_effect=lambda query, user_id, page_filter: query,
            ) as build_filter,
        ):
            result = await repository.summary_order_by(
                user_id=user_id,
                order_by=None,
                page_filter=None,
            )

        assert result is None

        only_filter_date.assert_called_once_with(None)

        build_filter.assert_called_once_with(
            ANY,
            user_id,
            None,
        )

        session.scalars.assert_awaited_once()
        scalars_result.first.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_use_desc_when_order_by_is_invalid():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()

        scalars_result = MagicMock()
        scalars_result.first.return_value = None
        session.scalars.return_value = scalars_result

        with (
            patch.object(
                repository,
                "_only_filter_date",
                return_value=None,
            ),
            patch.object(
                repository,
                "_build_filter",
                side_effect=lambda query, user_id, page_filter: query,
            ),
        ):
            result = await repository.summary_order_by(
                user_id=user_id,
                order_by="invalid",
                page_filter=None,
            )

        assert result is None

        session.scalars.assert_awaited_once()
        scalars_result.first.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_apply_only_date_filters():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()

        page_filter = FilterPage.build(
            beneficiary="Amazon",
            source_institution="Itaú",
            destination_institution="Nubank",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        expected_page_filter = FilterPage.build(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        scalars_result = MagicMock()
        scalars_result.first.return_value = None
        session.scalars.return_value = scalars_result

        with (
            patch.object(
                repository,
                "_only_filter_date",
                return_value=expected_page_filter,
            ) as only_filter_date,
            patch.object(
                repository,
                "_build_filter",
                side_effect=lambda query, user_id, page_filter: query,
            ) as build_filter,
        ):
            result = await repository.summary_order_by(
                user_id=user_id,
                order_by="desc",
                page_filter=page_filter,
            )

        assert result is None

        only_filter_date.assert_called_once_with(page_filter)

        build_filter.assert_called_once_with(
            ANY,
            user_id,
            expected_page_filter,
        )

        session.scalars.assert_awaited_once()
        scalars_result.first.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_pass_none_to_build_filter_when_page_filter_is_none():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()

        scalars_result = MagicMock()
        scalars_result.first.return_value = None
        session.scalars.return_value = scalars_result

        with (
            patch.object(
                repository,
                "_only_filter_date",
                return_value=None,
            ) as only_filter_date,
            patch.object(
                repository,
                "_build_filter",
                side_effect=lambda query, user_id, page_filter: query,
            ) as build_filter,
        ):
            result = await repository.summary_order_by(
                user_id=user_id,
                order_by="desc",
                page_filter=None,
            )

        assert result is None

        only_filter_date.assert_called_once_with(None)

        build_filter.assert_called_once_with(
            ANY,
            user_id,
            None,
        )

        session.scalars.assert_awaited_once()
        scalars_result.first.assert_called_once_with()


class TestPaymentRepositorySummaryBeneficiary:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_beneficiary_of_payments_when_page_filter_is_none():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()

        list = [
            SimpleNamespace(id=uuid4(), amount=Decimal("4741.75")),
            SimpleNamespace(id=uuid4(), amount=Decimal("132.98")),
        ]

        expected = {
            "total": sum([item.amount for item in list]),
            "beneficiary": "Amazon",
        }

        scalars_result = MagicMock()
        scalars_result.all.return_value = list
        session.scalars.return_value = scalars_result

        with (
            patch.object(
                repository,
                "_build_filter",
                side_effect=lambda query, user_id, page_filter: query,
            ) as build_filter,
        ):
            result = await repository.summary_beneficiary(
                user_id=user_id,
                beneficiary="Amazon",
                page_filter=None,
            )

        assert result == expected

        build_filter.assert_called_once()

        session.scalars.assert_awaited_once()
        scalars_result.all.assert_called_once_with()


class TestPaymentRepositoryGetOrderColumn:
    def test_should_return_payment_date_column(self):
        result = PaymentRepository._get_order_column("payment_date")

        assert result is Payment.payment_date

    def test_should_return_amount_column(self):
        result = PaymentRepository._get_order_column("amount")

        assert result is Payment.amount

    def test_should_return_created_at_column_when_order_by_is_invalid(self):
        result = PaymentRepository._get_order_column("invalid")

        assert result is Payment.created_at

    def test_should_return_created_at_column_when_order_by_is_none(self):
        result = PaymentRepository._get_order_column()

        assert result is Payment.created_at


class TestPaymentRepositoryOrderBy:
    def test_should_order_by_payment_date_ascending(self):
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)
        page_filter = FilterPage.build(
            order="asc",
            order_by="payment_date",
        )

        result = repository._order_by(
            query=query,
            page_filter=page_filter,
        )

        compiled = result.compile()

        assert "payments.payment_date ASC" in str(compiled)

    def test_should_order_by_amount_descending(self):
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)
        page_filter = FilterPage.build(
            order="desc",
            order_by="amount",
        )

        result = repository._order_by(
            query=query,
            page_filter=page_filter,
        )

        compiled = result.compile()

        assert "payments.amount DESC" in str(compiled)

    def test_should_order_by_created_at_when_order_by_is_invalid(self):
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)
        page_filter = FilterPage.build(
            order="asc",
            order_by="invalid",
        )

        result = repository._order_by(
            query=query,
            page_filter=page_filter,
        )

        compiled = result.compile()

        assert "payments.created_at ASC" in str(compiled)

    def test_should_apply_default_order_when_order_and_order_by_are_none(self):
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)
        page_filter = FilterPage()

        expected = MagicMock()

        with patch.object(
            repository,
            "_apply_order_by",
            return_value=expected,
        ) as apply_order_by:
            result = repository._order_by(
                query=query,
                page_filter=page_filter,
            )

        assert result is expected

        apply_order_by.assert_called_once_with(
            query=query,
            page_filter=page_filter,
        )

    def test_should_apply_default_order_when_page_filter_is_none(self):
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)

        expected = MagicMock()

        with patch.object(
            repository,
            "_apply_order_by",
            return_value=expected,
        ) as apply_order_by:
            result = repository._order_by(
                query=query,
                page_filter=None,
            )

        assert result is expected

        apply_order_by.assert_called_once_with(
            query=query,
            page_filter=None,
        )


class TestPaymentRepositoryBuildDashboardFilter:
    def test_should_filter_by_user_and_date_range(self):
        user_id = uuid4()
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)

        result = repository._build_dashboard_filter(
            query=query,
            user_id=user_id,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        compiled = result.compile(
            compile_kwargs={"literal_binds": True},
        )
        sql = str(compiled)

        assert f"payments.user_id = '{user_id.hex}'" in sql
        assert "payments.payment_date >= '2026-09-01'" in sql
        assert "payments.payment_date <= '2026-09-30'" in sql
        assert "JOIN institutions" not in sql

    def test_should_filter_by_institution(self):
        user_id = uuid4()
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)

        result = repository._build_dashboard_filter(
            query=query,
            user_id=user_id,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            institution="Itaú Unibanco",
        )

        compiled = result.compile(
            compile_kwargs={"literal_binds": True},
        )
        sql = str(compiled)

        assert f"payments.user_id = '{user_id.hex}'" in sql
        assert "payments.payment_date >= '2026-09-01'" in sql
        assert "payments.payment_date <= '2026-09-30'" in sql
        assert "JOIN institutions" in sql
        assert "institutions.name_code = 'itau_unibanco'" in sql

    def test_should_filter_by_beneficiary(self):
        user_id = uuid4()
        beneficiary_id = uuid4()
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)

        result = repository._build_dashboard_filter(
            query=query,
            user_id=user_id,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            beneficiary_id=beneficiary_id,
        )

        compiled = result.compile(
            compile_kwargs={"literal_binds": True},
        )
        sql = str(compiled)

        assert f"payments.user_id = '{user_id.hex}'" in sql
        assert "payments.payment_date >= '2026-09-01'" in sql
        assert "payments.payment_date <= '2026-09-30'" in sql
        assert f"payments.beneficiary_id = '{beneficiary_id.hex}'" in sql
        assert "JOIN institutions" not in sql

    def test_should_apply_all_dashboard_filters(self):
        user_id = uuid4()
        beneficiary_id = uuid4()
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)

        result = repository._build_dashboard_filter(
            query=query,
            user_id=user_id,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            institution="Itaú Unibanco",
            beneficiary_id=beneficiary_id,
        )

        compiled = result.compile(
            compile_kwargs={"literal_binds": True},
        )
        sql = str(compiled)

        assert f"payments.user_id = '{user_id.hex}'" in sql
        assert "payments.payment_date >= '2026-09-01'" in sql
        assert "payments.payment_date <= '2026-09-30'" in sql
        assert "JOIN institutions" in sql
        assert "institutions.name_code = 'itau_unibanco'" in sql
        assert f"payments.beneficiary_id = '{beneficiary_id.hex}'" in sql

    def test_should_not_apply_optional_dashboard_filters_when_not_provided(self):
        user_id = uuid4()
        session = AsyncMock()
        repository = PaymentRepository(session)

        query = select(Payment)

        result = repository._build_dashboard_filter(
            query=query,
            user_id=user_id,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            institution=None,
            beneficiary_id=None,
        )

        compiled = result.compile(
            compile_kwargs={"literal_binds": True},
        )
        sql = str(compiled)

        assert f"payments.user_id = '{user_id.hex}'" in sql
        assert "payments.payment_date >= '2026-09-01'" in sql
        assert "payments.payment_date <= '2026-09-30'" in sql
        assert "JOIN institutions" not in sql


class TestPaymentRepositoryDashboardSummary:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_dashboard_summary():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()
        start_date = date(2026, 9, 1)
        end_date = date(2026, 9, 30)
        institution = "Itaú"
        beneficiary_id = uuid4()

        row = SimpleNamespace(
            count=10,
            total=Decimal("5000.00"),
            average=Decimal("500.00"),
            highest=Decimal("1500.00"),
        )

        execute_result = MagicMock()
        execute_result.one.return_value = row
        session.execute.return_value = execute_result

        filtered_query = MagicMock()

        with patch.object(
            repository,
            "_build_dashboard_filter",
            return_value=filtered_query,
        ) as build_filter:
            result = await repository.dashboard_summary(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                institution=institution,
                beneficiary_id=beneficiary_id,
            )

        assert result == {
            "count": 10,
            "total": Decimal("5000.00"),
            "average": Decimal("500.00"),
            "highest": Decimal("1500.00"),
        }

        build_filter.assert_called_once_with(
            query=ANY,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            institution=institution,
            beneficiary_id=beneficiary_id,
        )

        session.execute.assert_awaited_once_with(
            filtered_query,
        )

        execute_result.one.assert_called_once_with()

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_dashboard_summary_with_zero_values():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()

        row = SimpleNamespace(
            count=0,
            total=Decimal("0"),
            average=Decimal("0"),
            highest=Decimal("0"),
        )

        execute_result = MagicMock()
        execute_result.one.return_value = row
        session.execute.return_value = execute_result

        with patch.object(
            repository,
            "_build_dashboard_filter",
            side_effect=lambda query, **kwargs: query,
        ):
            result = await repository.dashboard_summary(
                user_id=user_id,
                start_date=date(2026, 9, 1),
                end_date=date(2026, 9, 30),
            )

        assert result == {
            "count": 0,
            "total": Decimal("0"),
            "average": Decimal("0"),
            "highest": Decimal("0"),
        }


class TestPaymentRepositoryDashboardMonthly:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_dashboard_monthly():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()
        start_date = date(2026, 1, 1)
        end_date = date(2026, 9, 30)

        rows = [
            SimpleNamespace(
                period="2026-01",
                count=2,
                total=Decimal("1000.00"),
            ),
            SimpleNamespace(
                period="2026-02",
                count=3,
                total=Decimal("2000.00"),
            ),
        ]

        execute_result = MagicMock()
        execute_result.__iter__.return_value = iter(rows)
        session.execute.return_value = execute_result

        filtered_query = MagicMock()

        with patch.object(
            repository,
            "_build_dashboard_filter",
            return_value=filtered_query,
        ) as build_filter:
            result = await repository.dashboard_monthly(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                institution="Itaú",
                beneficiary_id=uuid4(),
            )

        assert result == [
            {
                "period": "2026-01",
                "count": 2,
                "total": Decimal("1000.00"),
            },
            {
                "period": "2026-02",
                "count": 3,
                "total": Decimal("2000.00"),
            },
        ]

        build_filter.assert_called_once_with(
            query=ANY,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            institution="Itaú",
            beneficiary_id=ANY,
        )

        session.execute.assert_awaited_once_with(
            filtered_query.group_by.return_value.order_by.return_value,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_there_are_no_monthly_results():
        session = AsyncMock()
        repository = PaymentRepository(session)

        execute_result = MagicMock()
        execute_result.__iter__.return_value = iter([])
        session.execute.return_value = execute_result

        with patch.object(
            repository,
            "_build_dashboard_filter",
            side_effect=lambda query, **kwargs: query,
        ):
            result = await repository.dashboard_monthly(
                user_id=uuid4(),
                start_date=date(2026, 9, 1),
                end_date=date(2026, 9, 30),
            )

        assert result == []


class TestPaymentRepositoryDashboardInstitutions:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_dashboard_institutions():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()
        institution_id = uuid4()

        rows = [
            SimpleNamespace(
                institution_id=institution_id,
                institution="itau",
                count=5,
                total=Decimal("3000.00"),
            ),
            SimpleNamespace(
                institution_id=uuid4(),
                institution="nubank",
                count=3,
                total=Decimal("1500.00"),
            ),
        ]

        execute_result = MagicMock()
        execute_result.__iter__.return_value = iter(rows)
        session.execute.return_value = execute_result

        filtered_query = MagicMock()

        with patch.object(
            repository,
            "_build_dashboard_filter",
            return_value=filtered_query,
        ) as build_filter:
            result = await repository.dashboard_institutions(
                user_id=user_id,
                start_date=date(2026, 1, 1),
                end_date=date(2026, 9, 30),
                institution="Itaú",
                beneficiary_id=uuid4(),
            )

        assert result == [
            {
                "institution_id": institution_id,
                "institution": "itau",
                "count": 5,
                "total": Decimal("3000.00"),
            },
            {
                "institution_id": rows[1].institution_id,
                "institution": "nubank",
                "count": 3,
                "total": Decimal("1500.00"),
            },
        ]

        build_filter.assert_called_once_with(
            query=ANY,
            user_id=user_id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 9, 30),
            institution="Itaú",
            beneficiary_id=ANY,
        )

        session.execute.assert_awaited_once_with(
            filtered_query.group_by.return_value.order_by.return_value,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_there_are_no_institution_results():
        session = AsyncMock()
        repository = PaymentRepository(session)

        execute_result = MagicMock()
        execute_result.__iter__.return_value = iter([])
        session.execute.return_value = execute_result

        with patch.object(
            repository,
            "_build_dashboard_filter",
            side_effect=lambda query, **kwargs: query,
        ):
            result = await repository.dashboard_institutions(
                user_id=uuid4(),
                start_date=date(2026, 9, 1),
                end_date=date(2026, 9, 30),
            )

        assert result == []


class TestPaymentRepositoryDashboardBeneficiaries:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_dashboard_beneficiaries():
        session = AsyncMock()
        repository = PaymentRepository(session)

        user_id = uuid4()
        beneficiary_id = uuid4()

        rows = [
            SimpleNamespace(
                beneficiary_id=beneficiary_id,
                name="Amazon",
                count=4,
                total=Decimal("2500.00"),
            ),
            SimpleNamespace(
                beneficiary_id=uuid4(),
                name="Mercado Livre",
                count=2,
                total=Decimal("800.00"),
            ),
        ]

        execute_result = MagicMock()
        execute_result.__iter__.return_value = iter(rows)
        session.execute.return_value = execute_result

        filtered_query = MagicMock()

        with patch.object(
            repository,
            "_build_dashboard_filter",
            return_value=filtered_query,
        ) as build_filter:
            result = await repository.dashboard_beneficiaries(
                user_id=user_id,
                start_date=date(2026, 1, 1),
                end_date=date(2026, 9, 30),
                institution="Itaú",
                beneficiary_id=beneficiary_id,
            )

        assert result == [
            {
                "beneficiary_id": beneficiary_id,
                "name": "Amazon",
                "count": 4,
                "total": Decimal("2500.00"),
            },
            {
                "beneficiary_id": rows[1].beneficiary_id,
                "name": "Mercado Livre",
                "count": 2,
                "total": Decimal("800.00"),
            },
        ]

        build_filter.assert_called_once_with(
            query=ANY,
            user_id=user_id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 9, 30),
            institution="Itaú",
            beneficiary_id=beneficiary_id,
        )

        session.execute.assert_awaited_once_with(
            filtered_query.group_by.return_value.order_by.return_value,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_there_are_no_beneficiary_results():
        session = AsyncMock()
        repository = PaymentRepository(session)

        execute_result = MagicMock()
        execute_result.__iter__.return_value = iter([])
        session.execute.return_value = execute_result

        with patch.object(
            repository,
            "_build_dashboard_filter",
            side_effect=lambda query, **kwargs: query,
        ):
            result = await repository.dashboard_beneficiaries(
                user_id=uuid4(),
                start_date=date(2026, 9, 1),
                end_date=date(2026, 9, 30),
            )

        assert result == []
