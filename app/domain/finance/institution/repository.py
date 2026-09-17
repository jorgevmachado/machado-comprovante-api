from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import Query
from sqlalchemy import or_, select

from app.core.pagination import is_paginate
from app.core.repository.base import BaseRepository
from app.models import Institution, Payment
from app.shared.schemas import FilterPage
from app.shared.utils.string import to_snake_case


class InstitutionRepository(BaseRepository[Institution]):
    model = Institution

    async def list(
        self,
        user_id: UUID,
        page_filter: Annotated[FilterPage, Query()] | None = None,
    ):
        query = (
            select(Institution)
            .join(
                Payment,
                or_(
                    Payment.source_institution_id == Institution.id,
                    Payment.destination_institution_id == Institution.id,
                ),
            )
            .where(Payment.user_id == user_id)
        )

        if page_filter is not None:
            raw_filter = page_filter.model_dump(exclude_none=True)

            name = cast(str, raw_filter.get("name"))
            institution_type = cast(str, raw_filter.get("institution_type"))

            if name:
                name_code = to_snake_case(name)

                query = query.where(Institution.name_code == name_code)

            if institution_type == "source":
                query = query.where(Payment.source_institution_id == Institution.id)

            if institution_type == "destination":
                query = query.where(
                    Payment.destination_institution_id == Institution.id
                )

        query = query.distinct()

        if page_filter is not None and is_paginate(page_filter):
            return await self.list_paginate(query, page_filter)

        result = await self.session.scalars(query)

        return result.all()
