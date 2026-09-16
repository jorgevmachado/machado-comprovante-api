from __future__ import annotations

from app.domain.finance.receipt.interpretation.interpreters.unknown import (
    UnknownInterpreter,
)
from app.domain.finance.receipt.interpretation.schema import (
    InstitutionEnum,
    InterpretationResult, ExtractedReceiptData, ExtractedField, ExtractionStatusEnum,
)
from app.domain.finance.receipt.interpretation.interpreters.caixa import (
    CaixaInterpreter,
)
from app.domain.finance.receipt.interpretation.interpreters.itau import ItauInterpreter
from app.domain.finance.receipt.interpretation.interpreters.nubank import (
    NubankInterpreter,
)
from app.domain.finance.receipt.interpretation.validation import InterpretationValidator


class InterpretationService:
    def __init__(self):
        self.itau = ItauInterpreter()
        self.nubank = NubankInterpreter()
        self.caixa = CaixaInterpreter()
        self.unknown = UnknownInterpreter()

    def interpret(self, text: str) -> InterpretationResult:
        if not self._has_text(text):
            data = self.unknown.invalid_interpret()
            return InterpretationValidator.validate(data)

        institution = self._identify_institution(text)

        if institution == InstitutionEnum.ITAU:
            data = self.itau.interpret(text)
            return InterpretationValidator.validate(data)

        if institution == InstitutionEnum.NUBANK:
            data = self.nubank.interpret(text)
            return InterpretationValidator.validate(data)

        if institution == InstitutionEnum.CAIXA:
            data = self.caixa.interpret(text)
            return InterpretationValidator.validate(data)

        data = self.unknown.interpret(text)
        return InterpretationValidator.validate(data)

    def convert(self, data: dict[str, object]) -> ExtractedReceiptData:
        return ExtractedReceiptData(
            payment_date=self._convert_field(data.get("payment_date")),
            document_amount=self._convert_field(data.get("document_amount")),
            paid_amount=self._convert_field(data.get("paid_amount")),
            beneficiary=self._convert_field(data.get("beneficiary")),
            source_institution=self._convert_field(
                data.get("source_institution")
            ),
            destination_institution=self._convert_field(
                data.get("destination_institution")
            ),
            due_date=self._convert_field(data.get("due_date")),
            discount=self._convert_field(data.get("discount")),
            interest=self._convert_field(data.get("interest")),
            fine=self._convert_field(data.get("fine")),
            total_charges=self._convert_field(data.get("total_charges")),
            payer=self._convert_field(data.get("payer")),
            effective_payer=self._convert_field(
                data.get("effective_payer")
            ),
            barcode=self._convert_field(data.get("barcode")),
            authentication=self._convert_field(
                data.get("authentication")
            ),
            transaction_id=self._convert_field(
                data.get("transaction_id")
            ),
        )

    @staticmethod
    def _convert_field(value: object) -> ExtractedField:
        return ExtractedField(
            value=value,
            status=(
                ExtractionStatusEnum.FOUND
                if value is not None
                else ExtractionStatusEnum.NOT_FOUND
            ),
        )

    @staticmethod
    def _identify_institution(text: str) -> InstitutionEnum:
        normalized_text = text.upper()

        if (
            "ITAU UNIBANCO" in normalized_text
            or "ITAÚ UNIBANCO" in normalized_text
            or "AUTENTICAÇÃO DIGITAL ITAÚ" in normalized_text
        ):
            return InstitutionEnum.ITAU

        if (
            "NU PAGAMENTOS SA" in normalized_text
            or "NU PAGAMENTOS S.A." in normalized_text
            or "NUBANK.COM.BR" in normalized_text
        ):
            return InstitutionEnum.NUBANK

        if (
            "CAIXA ECONOMICA FEDERAL" in normalized_text
            or "CAIXA ECONÔMICA FEDERAL" in normalized_text
            or "VIA INTERNET BANKING CAIXA" in normalized_text
        ):
            return InstitutionEnum.CAIXA

        return InstitutionEnum.UNKNOWN

    @staticmethod
    def _has_text(text: str) -> bool:
        return bool(text.strip())