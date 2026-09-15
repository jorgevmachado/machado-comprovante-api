from app.domain.finance.receipt.interpretation.interpreters.caixa import (
    CaixaInterpreter,
)
from app.domain.finance.receipt.interpretation.schema import (
    ExtractionStatusEnum,
)


class TestCaixaInterpreter:
    def test_extract_source_institution_from_caixa_format(self):
        text = """\
Banco Recebedor: CAIXA ECONOMICA FEDERAL
Pagador Final / Efetivo
CPF: 999.999.999-99
Nome: NOME QUALQUER
"""

        result = CaixaInterpreter._extract_source_institution(text)

        assert result.status == ExtractionStatusEnum.FOUND
        assert result.value == "Caixa"

    def test_extract_source_institution_supports_accented_caixa_name(self):
        text = """\
Banco Recebedor: CAIXA ECONÔMICA FEDERAL
Pagador Final / Efetivo
CPF: 999.999.999-99
Nome: NOME QUALQUER
"""

        result = CaixaInterpreter._extract_source_institution(text)

        assert result.status == ExtractionStatusEnum.FOUND
        assert result.value == "Caixa"

    def test_extract_source_institution_returns_bank_name_when_not_caixa(
        self,
    ):
        text = """\
Banco Recebedor: BANCO EXEMPLO S/A
Pagador Final / Efetivo
CPF: 999.999.999-99
Nome: NOME QUALQUER
"""

        result = CaixaInterpreter._extract_source_institution(text)

        assert result.status == ExtractionStatusEnum.FOUND
        assert result.value == "BANCO EXEMPLO S/A"

    def test_extract_source_institution_returns_not_found_without_bank_receiver(
        self,
    ):
        text = """\
Pagador Final / Efetivo
CPF: 999.999.999-99
Nome: NOME QUALQUER
"""

        result = CaixaInterpreter._extract_source_institution(text)

        assert result.status == ExtractionStatusEnum.NOT_FOUND
        assert result.value is None
