from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date
from decimal import Decimal

from app.domain.finance.beneficiary.schema import BeneficiarySchema
from app.domain.finance.institution.schema import InstitutionSchema


class PaymentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    amount: Decimal
    beneficiary: BeneficiarySchema
    payment_date: date
    source_institution: InstitutionSchema
    destination_institution: InstitutionSchema | None = None


class PaymentSummaryCountSchema(BaseModel):
    count: int


class PaymentSummaryTotalSchema(BaseModel):
    total: Decimal


class PaymentSummaryMinMaxSchema(BaseModel):
    payment: PaymentSchema | None = None
    model_config = ConfigDict(from_attributes=True)


class PaymentSummaryBeneficiaryTotalSchema(BaseModel):
    total: Decimal
    beneficiary: str
