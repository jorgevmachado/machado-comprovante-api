from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import handle_service_exception
from app.core.logging import LoggingParams, log_service_success
from app.core.pagination import exception_pagination
from app.core.service import BaseService
from app.domain.finance.institution.repository import InstitutionRepository
from app.domain.finance.institution.schema import InstitutionSchema

from app.models import Institution, User
from app.shared.schemas import FilterPage
from app.shared.utils.string import to_snake_case

logger = logging.getLogger(__name__)


class InstitutionService(BaseService[InstitutionRepository, Institution]):
    def __init__(self, repository: InstitutionRepository) -> None:
        super().__init__(
            alias="Institution",
            repository=repository,
            logger_params=LoggingParams(
                logger=logger, service="InstitutionService", operation="institution"
            ),
            schema_class=InstitutionSchema,
            cache_prefix="institution",
        )

    @classmethod
    def from_session(cls, session: AsyncSession) -> InstitutionService:
        return cls(InstitutionRepository(session))

    async def resolve(self, name: str):
        name_code = to_snake_case(name)
        institution = await self.find_by(name_code=name_code, without_throw=True)
        if not institution:
            return await self.repository.save(
                entity=Institution(name=name, name_code=name_code)
            )
        return institution

    async def list(
        self,
        user: User,
        page_filter: Annotated[FilterPage, Query()] | None = None,
    ):
        try:
            return await self.repository.list(
                user_id=user.id, page_filter=page_filter
            )
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