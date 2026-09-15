from app.domain.finance.receipt.interpretation.interpreters.itau import (
    ItauInterpreter,
)
from app.domain.finance.receipt.interpretation.schema import (
    ExtractionStatusEnum,
)


class TestItauInterpreter:
    def test_extract_authentication(self):
        result = ItauInterpreter._extract_authentication("Autenticação: ABC123XYZ789")

        assert result.status == ExtractionStatusEnum.FOUND
        assert result.value == "ABC123XYZ789"

    def test_extract_authentication_supports_digital_itau_format(self):
        result = ItauInterpreter._extract_authentication(
            "Autenticação digital Itaú: XYZ789ABC123"
        )

        assert result.status == ExtractionStatusEnum.FOUND
        assert result.value == "XYZ789ABC123"

    def test_extract_authentication_returns_not_found_without_authentication(
        self,
    ):
        result = ItauInterpreter._extract_authentication("Comprovante de pagamento")

        assert result.status == ExtractionStatusEnum.NOT_FOUND
        assert result.value is None

    def test_extract_source_institution_from_itau_unibanco(self):
        result = ItauInterpreter._extract_source_institution(
            "Beneficiário: ITAU UNIBANCO S.A."
        )

        assert result.status == ExtractionStatusEnum.FOUND
        assert result.value == "Itaú"

    def test_extract_source_institution_from_accented_itau_unibanco(self):
        result = ItauInterpreter._extract_source_institution(
            "Beneficiário: ITAÚ UNIBANCO S.A."
        )

        assert result.status == ExtractionStatusEnum.FOUND
        assert result.value == "Itaú"

    def test_extract_source_institution_from_digital_authentication(self):
        result = ItauInterpreter._extract_source_institution(
            "AUTENTICAÇÃO DIGITAL ITAÚ: ABC123XYZ"
        )

        assert result.status == ExtractionStatusEnum.FOUND
        assert result.value == "Itaú"

    def test_extract_source_institution_returns_not_found_when_itau_is_absent(
        self,
    ):
        result = ItauInterpreter._extract_source_institution(
            "Beneficiário: BANCO EXEMPLO S.A."
        )

        assert result.status == ExtractionStatusEnum.NOT_FOUND
        assert result.value is None
