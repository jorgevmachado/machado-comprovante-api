from pydantic import BaseModel
from uuid import UUID
from datetime import date
from decimal import Decimal

from app.domain.finance.beneficiary.schema import BeneficiarySchema
from app.domain.finance.institution.schema import InstitutionSchema


class PaymentSchema(BaseModel):
    id: UUID
    amount: Decimal
    beneficiary: BeneficiarySchema
    payment_date: date
    source_institution: InstitutionSchema
    destination_institution: InstitutionSchema | None = None
