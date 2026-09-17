from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.domain.finance.institution.repository import InstitutionRepository
from app.shared.schemas import FilterPage


class TestInstitutionRepositoryList:
    @staticmethod
    @pytest.mark.asyncio
    async def test_should_list_institutions_by_user():
        session = AsyncMock()
        repository = InstitutionRepository(session)

        scalars_result = MagicMock()
        expected = [
            MagicMock(),
            MagicMock(),
        ]
        scalars_result.all.return_value = expected
        session.scalars.return_value = scalars_result

        user_id = uuid4()

        with patch(
            "app.domain.finance.institution.repository.is_paginate",
            return_value=False,
        ):
            result = await repository.list(
                user_id=user_id,
                page_filter=None,
            )

        assert result is expected

        session.scalars.assert_awaited_once()

        query = session.scalars.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert f"payments.user_id = '{user_id.hex}'" in sql

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_not_apply_name_filter_when_name_is_not_provided():
        session = AsyncMock()
        repository = InstitutionRepository(session)

        scalars_result = MagicMock()
        scalars_result.all.return_value = []
        session.scalars.return_value = scalars_result

        user_id = uuid4()
        page_filter = FilterPage.build()

        with patch(
            "app.domain.finance.institution.repository.is_paginate",
            return_value=False,
        ):
            await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        query = session.scalars.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert "institutions.name_code =" not in sql

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_filter_by_name():
        session = AsyncMock()
        repository = InstitutionRepository(session)

        scalars_result = MagicMock()
        scalars_result.all.return_value = []
        session.scalars.return_value = scalars_result

        user_id = uuid4()
        page_filter = FilterPage.build(
            name="Itaú Unibanco",
        )

        with patch(
            "app.domain.finance.institution.repository.is_paginate",
            return_value=False,
        ), patch(
            "app.domain.finance.institution.repository.to_snake_case",
            return_value="itau_unibanco",
        ) as to_snake_case:
            await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        to_snake_case.assert_called_once_with("Itaú Unibanco")

        query = session.scalars.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert "institutions.name_code = 'itau_unibanco'" in sql

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_filter_by_source_institution():
        session = AsyncMock()
        repository = InstitutionRepository(session)

        scalars_result = MagicMock()
        scalars_result.all.return_value = []
        session.scalars.return_value = scalars_result

        user_id = uuid4()
        page_filter = FilterPage.build(
            institution_type="source",
        )

        with patch(
            "app.domain.finance.institution.repository.is_paginate",
            return_value=False,
        ):
            await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        query = session.scalars.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert (
            "payments.source_institution_id = institutions.id"
            in sql
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_filter_by_destination_institution():
        session = AsyncMock()
        repository = InstitutionRepository(session)

        scalars_result = MagicMock()
        scalars_result.all.return_value = []
        session.scalars.return_value = scalars_result

        user_id = uuid4()
        page_filter = FilterPage.build(
            institution_type="destination",
        )

        with patch(
            "app.domain.finance.institution.repository.is_paginate",
            return_value=False,
        ):
            await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        query = session.scalars.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert (
            "payments.destination_institution_id = institutions.id"
            in sql
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_filter_by_name_and_source():
        session = AsyncMock()
        repository = InstitutionRepository(session)

        scalars_result = MagicMock()
        scalars_result.all.return_value = []
        session.scalars.return_value = scalars_result

        user_id = uuid4()
        page_filter = FilterPage.build(
            name="Itaú",
            institution_type="source",
        )

        with patch(
            "app.domain.finance.institution.repository.is_paginate",
            return_value=False,
        ), patch(
            "app.domain.finance.institution.repository.to_snake_case",
            return_value="itau",
        ):
            await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        query = session.scalars.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert "institutions.name_code = 'itau'" in sql
        assert (
            "payments.source_institution_id = institutions.id"
            in sql
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_filter_by_name_and_destination():
        session = AsyncMock()
        repository = InstitutionRepository(session)

        scalars_result = MagicMock()
        scalars_result.all.return_value = []
        session.scalars.return_value = scalars_result

        user_id = uuid4()
        page_filter = FilterPage.build(
            name="Nubank",
            institution_type="destination",
        )

        with patch(
            "app.domain.finance.institution.repository.is_paginate",
            return_value=False,
        ), patch(
            "app.domain.finance.institution.repository.to_snake_case",
            return_value="nubank",
        ):
            await repository.list(
                user_id=user_id,
                page_filter=page_filter,
            )

        query = session.scalars.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert "institutions.name_code = 'nubank'" in sql
        assert (
            "payments.destination_institution_id = institutions.id"
            in sql
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_use_pagination_when_filter_is_paginated():
        session = AsyncMock()
        repository = InstitutionRepository(session)

        page_filter = FilterPage.build(
            page=1,
            limit=10,
        )

        expected = MagicMock()

        with patch(
            "app.domain.finance.institution.repository.is_paginate",
            return_value=True,
        ), patch.object(
            repository,
            "list_paginate",
            new_callable=AsyncMock,
            return_value=expected,
        ) as list_paginate:
            result = await repository.list(
                user_id=uuid4(),
                page_filter=page_filter,
            )

        assert result is expected

        list_paginate.assert_awaited_once()

        query = list_paginate.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert "SELECT DISTINCT" in sql

    @staticmethod
    @pytest.mark.asyncio
    async def test_should_use_distinct_when_listing_institutions():
        session = AsyncMock()
        repository = InstitutionRepository(session)

        scalars_result = MagicMock()
        scalars_result.all.return_value = []
        session.scalars.return_value = scalars_result

        with patch(
            "app.domain.finance.institution.repository.is_paginate",
            return_value=False,
        ):
            await repository.list(
                user_id=uuid4(),
                page_filter=None,
            )

        query = session.scalars.await_args.args[0]

        compiled = query.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        assert "SELECT DISTINCT" in sql
