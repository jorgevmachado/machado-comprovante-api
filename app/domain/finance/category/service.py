from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import handle_service_exception
from app.core.logging import LoggingParams, log_service_success
from app.core.pagination import exception_pagination
from app.core.service import BaseService

from app.models import Category, User

from app.domain.finance.category.repository import CategoryRepository
from app.domain.finance.category.schema import CategorySchema
from app.shared.schemas import FilterPage
from app.shared.utils.string import to_snake_case

logger = logging.getLogger(__name__)

class CategoryService(BaseService[CategoryRepository, Category]):
    def __init__(self,repository: CategoryRepository) -> None:
        super().__init__(
            alias="Category",
            repository=repository,
            logger_params=LoggingParams(
                logger=logger,
                service="CategoryService",
                operation="category"
            ),
            schema_class=CategorySchema,
            cache_prefix="category"
        )

    @classmethod
    def from_session(cls, session: AsyncSession) -> CategoryService:
        return cls(CategoryRepository(session))

    async def create(self, user_id: UUID, name: str, name_code: str | None = None, description: str | None = None) -> Category:
        if name_code is None:
            name_code = to_snake_case(name)
            category = await self.find_by(user_id=user_id, name_code=name_code, without_throw=True)
            if category:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT, detail="Category already exists"
                )
        return await self.repository.save(
            entity=Category(
                user_id=user_id,
                name=name,
                name_code=name_code,
                description=description
            )
        )

    async def resolve(self, user_id:UUID, name: str):
        name_code = to_snake_case(name)
        entity = await self.find_by(user_id=user_id, name_code=name_code, without_throw=True)
        if not entity:
            return await self.create(
                user_id=user_id,
                name=name,
                name_code=name_code
            )
        return entity

    async def list(
        self,
        user: User,
        page_filter: Annotated[FilterPage, Query()] | None = None,
    ):
        try:
            return await self.repository.list(user_id=user.id, page_filter=page_filter)
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation="list",
                user_request=user.username,
                raise_exception=False,
            )
            return exception_pagination(page_filter)
        finally:
            log_service_success(
                self.logger_params,
                operation="list",
                message="List successfully",
                user_request=user.username,
            )
