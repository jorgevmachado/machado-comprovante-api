from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import LoggingParams
from app.core.service import BaseService
from app.domain.finance.beneficiary.repository import BeneficiaryRepository
from app.domain.finance.beneficiary.schema import BeneficiarySchema

from app.models import Beneficiary
from app.shared.utils.string import to_snake_case

logger = logging.getLogger(__name__)


class BeneficiaryService(BaseService[BeneficiaryRepository, Beneficiary]):
    def __init__(self, repository: BeneficiaryRepository) -> None:
        super().__init__(
            alias="Beneficiary",
            repository=repository,
            logger_params=LoggingParams(
                logger=logger, service="BeneficiaryService", operation="beneficiary"
            ),
            schema_class=BeneficiarySchema,
            cache_prefix="beneficiary",
        )

    @classmethod
    def from_session(cls, session: AsyncSession) -> BeneficiaryService:
        return cls(BeneficiaryRepository(session))

    async def resolve(self, name: str):
        name_code = to_snake_case(name)
        beneficiary = await self.find_by(name_code=name_code, without_throw=True)
        if not beneficiary:
            return await self.repository.save(
                entity=Beneficiary(name=name, name_code=name_code)
            )
        return beneficiary
