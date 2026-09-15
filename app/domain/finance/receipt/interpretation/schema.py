from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class InstitutionEnum(StrEnum):
    ITAU = "itau"
    CAIXA = "caixa"
    NUBANK = "nubank"
    UNKNOWN = "unknown"


class ExtractionStatusEnum(StrEnum):
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    AMBIGUOUS = "AMBIGUOUS"


class ExtractedField(BaseModel, Generic[T]):
    value: T | None = None
    status: ExtractionStatusEnum


class ExtractedReceiptData(BaseModel):
    fine: ExtractedField[Decimal]
    payer: ExtractedField[str]
    barcode: ExtractedField[str]
    due_date: ExtractedField[date]
    discount: ExtractedField[Decimal]
    interest: ExtractedField[Decimal]
    paid_amount: ExtractedField[Decimal]
    beneficiary: ExtractedField[str]
    payment_date: ExtractedField[date]
    total_charges: ExtractedField[Decimal]
    authentication: ExtractedField[str]
    transaction_id: ExtractedField[str]
    effective_payer: ExtractedField[str]
    document_amount: ExtractedField[Decimal]
    source_institution: ExtractedField[str]
    destination_institution: ExtractedField[str]


class InterpretationValidationError(BaseModel):
    field: str
    status: ExtractionStatusEnum


class InterpretationResult(BaseModel):
    data: ExtractedReceiptData
    errors: list[InterpretationValidationError]
