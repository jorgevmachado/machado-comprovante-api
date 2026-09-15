from unittest.mock import MagicMock

from app.domain.finance.receipt.interpretation.schema import (
    InstitutionEnum,
    InterpretationResult, ExtractedField, ExtractionStatusEnum,
)
from app.domain.finance.receipt.interpretation.service import (
    InterpretationService,
)


class TestInterpretationService:
    def test_identify_itau_by_unibanco_name(self):
        result = InterpretationService._identify_institution(
            "Instituição: ITAU UNIBANCO S.A."
        )

        assert result == InstitutionEnum.ITAU

    def test_identify_itau_by_accented_unibanco_name(self):
        result = InterpretationService._identify_institution(
            "Instituição: ITAÚ UNIBANCO S.A."
        )

        assert result == InstitutionEnum.ITAU

    def test_identify_itau_by_digital_authentication(self):
        result = InterpretationService._identify_institution(
            "AUTENTICAÇÃO DIGITAL ITAÚ: ABC123"
        )

        assert result == InstitutionEnum.ITAU

    def test_identify_nubank_by_nu_pagamentos(self):
        result = InterpretationService._identify_institution(
            "Favorecido: NU PAGAMENTOS SA"
        )

        assert result == InstitutionEnum.NUBANK

    def test_identify_nubank_by_nu_pagamentos_with_punctuation(self):
        result = InterpretationService._identify_institution(
            "Favorecido: NU PAGAMENTOS S.A."
        )

        assert result == InstitutionEnum.NUBANK

    def test_identify_nubank_by_domain(self):
        result = InterpretationService._identify_institution("Acesse NUBANK.COM.BR")

        assert result == InstitutionEnum.NUBANK

    def test_identify_caixa_by_economica_federal(self):
        result = InterpretationService._identify_institution(
            "Banco Recebedor: CAIXA ECONOMICA FEDERAL"
        )

        assert result == InstitutionEnum.CAIXA

    def test_identify_caixa_by_accented_economica_federal(self):
        result = InterpretationService._identify_institution(
            "Banco Recebedor: CAIXA ECONÔMICA FEDERAL"
        )

        assert result == InstitutionEnum.CAIXA

    def test_identify_caixa_by_internet_banking(self):
        result = InterpretationService._identify_institution(
            "Via Internet Banking CAIXA"
        )

        assert result == InstitutionEnum.CAIXA

    def test_identify_unknown_institution(self):
        result = InterpretationService._identify_institution("Banco Exemplo S.A.")

        assert result == InstitutionEnum.UNKNOWN

    def test_interpret_uses_itau_interpreter(self):
        service = InterpretationService()

        expected = MagicMock(spec=InterpretationResult)

        service.itau.interpret = MagicMock(return_value=MagicMock())
        service.unknown.interpret = MagicMock()

        from app.domain.finance.receipt.interpretation.service import (
            InterpretationValidator,
        )

        original_validate = InterpretationValidator.validate

        try:
            InterpretationValidator.validate = MagicMock(
                return_value=expected,
            )

            result = service.interpret("ITAU UNIBANCO S.A.")

            assert result is expected
            service.itau.interpret.assert_called_once_with("ITAU UNIBANCO S.A.")
            service.unknown.interpret.assert_not_called()
        finally:
            InterpretationValidator.validate = original_validate

    def test_interpret_uses_nubank_interpreter(self):
        service = InterpretationService()

        expected = MagicMock(spec=InterpretationResult)

        service.nubank.interpret = MagicMock(return_value=MagicMock())

        from app.domain.finance.receipt.interpretation.service import (
            InterpretationValidator,
        )

        original_validate = InterpretationValidator.validate

        try:
            InterpretationValidator.validate = MagicMock(
                return_value=expected,
            )

            result = service.interpret("NU PAGAMENTOS S.A.")

            assert result is expected
            service.nubank.interpret.assert_called_once_with("NU PAGAMENTOS S.A.")
        finally:
            InterpretationValidator.validate = original_validate

    def test_interpret_uses_caixa_interpreter(self):
        service = InterpretationService()

        expected = MagicMock(spec=InterpretationResult)

        service.caixa.interpret = MagicMock(return_value=MagicMock())

        from app.domain.finance.receipt.interpretation.service import (
            InterpretationValidator,
        )

        original_validate = InterpretationValidator.validate

        try:
            InterpretationValidator.validate = MagicMock(
                return_value=expected,
            )

            result = service.interpret("CAIXA ECONOMICA FEDERAL")

            assert result is expected
            service.caixa.interpret.assert_called_once_with("CAIXA ECONOMICA FEDERAL")
        finally:
            InterpretationValidator.validate = original_validate

    def test_interpret_uses_unknown_interpreter(self):
        service = InterpretationService()

        expected = MagicMock(spec=InterpretationResult)

        service.unknown.interpret = MagicMock(return_value=MagicMock())

        from app.domain.finance.receipt.interpretation.service import (
            InterpretationValidator,
        )

        original_validate = InterpretationValidator.validate

        try:
            InterpretationValidator.validate = MagicMock(
                return_value=expected,
            )

            result = service.interpret("BANCO EXEMPLO S.A.")

            assert result is expected
            service.unknown.interpret.assert_called_once_with("BANCO EXEMPLO S.A.")
        finally:
            InterpretationValidator.validate = original_validate

    @staticmethod
    def test_convert_field_returns_found_when_value_exists():
        value = "Empresa Exemplo"

        result = InterpretationService._convert_field(value)

        assert isinstance(result, ExtractedField)
        assert result.value == value
        assert result.status == ExtractionStatusEnum.FOUND

    @staticmethod
    def test_convert_field_returns_not_found_when_value_is_none():
        result = InterpretationService._convert_field(None)

        assert isinstance(result, ExtractedField)
        assert result.value is None
        assert result.status == ExtractionStatusEnum.NOT_FOUND