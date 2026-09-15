from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.domain.finance.beneficiary.schema import BeneficiarySchema
from app.domain.finance.payment.schema import PaymentSchema
from app.domain.finance.institution.schema import InstitutionSchema


class FinanceConfirmRequestSchema(BaseModel):
    beneficiary: str
    paid_amount: Decimal
    payment_date: date
    source_institution: str
    destination_institution: str | None = None

    fine: Decimal | None = None
    payer: str | None = None
    barcode: str | None = None
    due_date: date | None = None
    discount: Decimal | None = None
    interest: Decimal | None = None
    total_charges: Decimal | None = None
    authentication: str | None = None
    transaction_id: str | None = None
    effective_payer: str | None = None
    document_amount: Decimal | None = None


class FinanceConfirmResponseSchema(BaseModel):
    payment: PaymentSchema
    beneficiary: BeneficiarySchema
    source_institution: InstitutionSchema
    destination_institution: InstitutionSchema | None = None
