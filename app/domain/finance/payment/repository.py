from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload


from fastapi import Query

from app.core.pagination import is_paginate
from app.core.repository.base import BaseRepository
from app.models import Beneficiary, Institution, Payment
from app.shared.schemas import FilterPage
from app.shared.utils.string import to_snake_case


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    @staticmethod
    def _build_filter(
        query, user_id: UUID, page_filter: Annotated[FilterPage, Query()] | None = None
    ):
        relations = {
            "beneficiary": Beneficiary,
            "destination_institution": Institution,
            "source_institution": Institution,
        }
        query = query.where(Payment.user_id == user_id)
        if page_filter is None:
            return query
        raw_filters = page_filter.model_dump(exclude_none=True)
        for relation, model in relations.items():
            if raw_filters.get(relation):
                relation_name = cast(str, raw_filters.get(relation))
                relation_name_code = to_snake_case(relation_name)

                query = query.join(getattr(Payment, relation)).where(
                    model.name_code == relation_name_code
                )
        if raw_filters.get("start_date"):
            query = query.where(Payment.payment_date >= raw_filters.get("start_date"))
            raw_filters.pop("start_date")
        if raw_filters.get("end_date"):
            query = query.where(Payment.payment_date <= raw_filters.get("end_date"))
            raw_filters.pop("end_date")
        return query

    async def list(
        self, user_id: UUID, page_filter: Annotated[FilterPage, Query()] | None = None
    ):
        query = select(self.model).options(
            selectinload(Payment.user),
            selectinload(Payment.beneficiary),
            selectinload(Payment.source_institution),
            selectinload(Payment.destination_institution),
        )
        query = self._build_filter(query, user_id, page_filter)
        query = self._apply_order_by(query, page_filter)
        if page_filter is not None and is_paginate(page_filter):
            return await self.list_paginate(query, page_filter)
        result = await self.session.scalars(query)
        return result.all()
