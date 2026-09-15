from datetime import date
from decimal import Decimal

from app.domain.finance.receipt.interpretation.schema import (
    ExtractedField,
    ExtractedReceiptData,
    ExtractionStatusEnum,
)
from app.domain.finance.receipt.interpretation.validation import (
    InterpretationValidator,
)


def build_data(
    *,
    payment_date_status: ExtractionStatusEnum = ExtractionStatusEnum.FOUND,
    paid_amount_status: ExtractionStatusEnum = ExtractionStatusEnum.FOUND,
    beneficiary_status: ExtractionStatusEnum = ExtractionStatusEnum.FOUND,
    source_institution_status: ExtractionStatusEnum = ExtractionStatusEnum.FOUND,
) -> ExtractedReceiptData:
    return ExtractedReceiptData(
        payment_date=ExtractedField(
            value=date(2026, 9, 15),
            status=payment_date_status,
        ),
        document_amount=ExtractedField(
            value=Decimal("100.00"),
            status=ExtractionStatusEnum.FOUND,
        ),
        paid_amount=ExtractedField(
            value=Decimal("95.00"),
            status=paid_amount_status,
        ),
        beneficiary=ExtractedField(
            value="EMPRESA EXEMPLO",
            status=beneficiary_status,
        ),
        source_institution=ExtractedField(
            value="Banco Exemplo",
            status=source_institution_status,
        ),
        destination_institution=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        due_date=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        discount=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        interest=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        fine=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        total_charges=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        payer=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        effective_payer=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        barcode=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        authentication=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        transaction_id=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
    )


class TestInterpretationValidator:
    def test_validate_returns_no_errors_when_required_fields_are_found(self):
        data = build_data()

        result = InterpretationValidator.validate(data)

        assert result.data == data
        assert result.errors == []

    def test_validate_returns_error_when_payment_date_is_not_found(self):
        data = build_data(
            payment_date_status=ExtractionStatusEnum.NOT_FOUND,
        )

        result = InterpretationValidator.validate(data)

        assert len(result.errors) == 1
        assert result.errors[0].field == "payment_date"
        assert result.errors[0].status == ExtractionStatusEnum.NOT_FOUND

    def test_validate_returns_error_when_paid_amount_is_not_found(self):
        data = build_data(
            paid_amount_status=ExtractionStatusEnum.NOT_FOUND,
        )

        result = InterpretationValidator.validate(data)

        assert len(result.errors) == 1
        assert result.errors[0].field == "paid_amount"
        assert result.errors[0].status == ExtractionStatusEnum.NOT_FOUND

    def test_validate_returns_error_when_beneficiary_is_not_found(self):
        data = build_data(
            beneficiary_status=ExtractionStatusEnum.NOT_FOUND,
        )

        result = InterpretationValidator.validate(data)

        assert len(result.errors) == 1
        assert result.errors[0].field == "beneficiary"
        assert result.errors[0].status == ExtractionStatusEnum.NOT_FOUND

    def test_validate_returns_error_when_source_institution_is_not_found(self):
        data = build_data(
            source_institution_status=ExtractionStatusEnum.NOT_FOUND,
        )

        result = InterpretationValidator.validate(data)

        assert len(result.errors) == 1
        assert result.errors[0].field == "source_institution"
        assert result.errors[0].status == ExtractionStatusEnum.NOT_FOUND

    def test_validate_returns_error_when_required_field_is_ambiguous(self):
        data = build_data(
            paid_amount_status=ExtractionStatusEnum.AMBIGUOUS,
        )

        result = InterpretationValidator.validate(data)

        assert len(result.errors) == 1
        assert result.errors[0].field == "paid_amount"
        assert result.errors[0].status == ExtractionStatusEnum.AMBIGUOUS

    def test_validate_returns_all_required_field_errors(self):
        data = build_data(
            payment_date_status=ExtractionStatusEnum.NOT_FOUND,
            paid_amount_status=ExtractionStatusEnum.AMBIGUOUS,
            beneficiary_status=ExtractionStatusEnum.NOT_FOUND,
            source_institution_status=ExtractionStatusEnum.AMBIGUOUS,
        )

        result = InterpretationValidator.validate(data)

        assert len(result.errors) == 4

        assert result.errors[0].field == "payment_date"
        assert result.errors[0].status == ExtractionStatusEnum.NOT_FOUND

        assert result.errors[1].field == "paid_amount"
        assert result.errors[1].status == ExtractionStatusEnum.AMBIGUOUS

        assert result.errors[2].field == "beneficiary"
        assert result.errors[2].status == ExtractionStatusEnum.NOT_FOUND

        assert result.errors[3].field == "source_institution"
        assert result.errors[3].status == ExtractionStatusEnum.AMBIGUOUS

    def test_validate_ignores_invalid_optional_fields(self):
        data = build_data()

        data.due_date = ExtractedField(
            value=None,
            status=ExtractionStatusEnum.AMBIGUOUS,
        )
        data.destination_institution = ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        )

        result = InterpretationValidator.validate(data)

        assert result.errors == []
