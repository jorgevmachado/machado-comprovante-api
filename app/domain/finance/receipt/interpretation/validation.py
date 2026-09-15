from __future__ import annotations

from app.domain.finance.receipt.interpretation.schema import (
    ExtractedReceiptData,
    ExtractionStatusEnum,
    InterpretationValidationError,
    InterpretationResult,
)


class InterpretationValidator:
    REQUIRED_FIELDS = (
        "payment_date",
        "paid_amount",
        "beneficiary",
        "source_institution",
    )

    @classmethod
    def validate(
        cls,
        data: ExtractedReceiptData,
    ) -> InterpretationResult:
        errors = [
            InterpretationValidationError(field=field_name, status=field.status)
            for field_name in cls.REQUIRED_FIELDS
            if (field := getattr(data, field_name)).status != ExtractionStatusEnum.FOUND
        ]
        return InterpretationResult(
            data=data,
            errors=errors,
        )
