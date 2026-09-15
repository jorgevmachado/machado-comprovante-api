from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import LoggingParams
from app.core.service import BaseService
from app.domain.finance.institution.repository import InstitutionRepository
from app.domain.finance.institution.schema import InstitutionSchema

from app.models import Institution
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
