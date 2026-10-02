from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from app.domain.finance.beneficiary.schema import BeneficiarySchema
from app.domain.finance.institution.schema import InstitutionSchema
from app.domain.finance.receipt.schema import ReceiptSchema


class PaymentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    amount: Decimal
    receipt: ReceiptSchema
    beneficiary: BeneficiarySchema
    payment_date: date
    created_at: datetime
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

class PaymentDashboardPeriodSchema(BaseModel):
    end_date: date
    start_date: date

class PaymentDashboardSummarySchema(BaseModel):
    total: Decimal
    count: int
    average: Decimal
    highest: Decimal

class PaymentDashboardMonthlySchema(BaseModel):
    total: Decimal
    count: int
    period: str

class PaymentDashboardInstitutionSchema(BaseModel):
    total: Decimal
    count: int
    institution: str

class PaymentDashboardBeneficiarySchema(BaseModel):
    name: str
    total: Decimal
    count: int
    beneficiary_id: UUID

class PaymentDashboardResponseSchema(BaseModel):
    period: PaymentDashboardPeriodSchema
    summary: PaymentDashboardSummarySchema
    monthly: list[PaymentDashboardMonthlySchema]
    institutions: list[PaymentDashboardInstitutionSchema]
    beneficiaries: list[PaymentDashboardBeneficiarySchema]

class PaymentDashboardRequestSchema(BaseModel):
    end_date: date
    start_date: date
    institution: str | None = None
    beneficiary_id: UUID | None = None