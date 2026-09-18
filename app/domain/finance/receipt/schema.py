from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date

from app.domain.finance.receipt.interpretation.schema import (
    ExtractedReceiptData,
    InterpretationValidationError,
)
from app.models import ProcessingStatusEnum


class ReceiptSchema(BaseModel):
    id: UUID
    file_name: str
    file_type: str
    file_size: int
    extracted_data: ExtractedReceiptData | None = None
    processing_status: ProcessingStatusEnum
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class UploadReceiptResponseSchema(BaseModel):
    id: UUID
    data: ExtractedReceiptData | None = None
    errors: list[InterpretationValidationError]
    file_name: str | None = None
    file_type: str | None = None
    file_size: int
    error_message: str | None = None
    processing_status: ProcessingStatusEnum


class BatchReceiptResponseSchema(BaseModel):
    total: int
    items: list[UploadReceiptResponseSchema]
    failed: int
    received: int
    processed: int
    processing: int


class ConfirmReceiptRequestSchema(BaseModel):
    payment_date: date
    amount: Decimal
    beneficiary: str
    source_institution: str
    destination_institution: str | None = None
