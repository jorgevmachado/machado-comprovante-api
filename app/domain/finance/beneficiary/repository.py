from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from sqlalchemy import select
from fastapi import Query

from app.core.pagination import is_paginate
from app.core.repository.base import BaseRepository
from app.models import (
    Beneficiary,
    Payment,
)
from app.shared.schemas import FilterPage
from app.shared.utils.string import to_snake_case


class BeneficiaryRepository(BaseRepository[Beneficiary]):
    model = Beneficiary

    async def list(
        self, user_id: UUID, page_filter: Annotated[FilterPage, Query()] | None = None
    ):
        query = (
            select(Beneficiary)
            .join(Beneficiary.payments)
            .where(Payment.user_id == user_id)
        )
        if page_filter is not None and is_paginate(page_filter):
            raw_filter = page_filter.model_dump(exclude_none=True)
            if raw_filter.get("name"):
                name = cast(str, raw_filter.get("name"))
                name_code = to_snake_case(name)
                query = query.where(Beneficiary.name_code == name_code)
            return await self.list_paginate(query.distinct(), page_filter)

        result = await self.session.scalars(query.distinct())
        return result.all()
