from __future__ import annotations

import re

from app.domain.finance.receipt.interpretation.interpreters.base import BaseInterpreter
from app.domain.finance.receipt.interpretation.schema import ExtractedField


class CaixaInterpreter(BaseInterpreter):
    @staticmethod
    def _extract_source_institution(text: str) -> ExtractedField[str]:
        match = re.search(
            r"Banco Recebedor:\s*(.+?)(?=\n|Pagador Final)",
            text,
            re.IGNORECASE,
        )

        if not match:
            return CaixaInterpreter._not_found()

        value = match.group(1).strip()

        if "CAIXA ECONOMICA FEDERAL" in value.upper():
            return CaixaInterpreter._extract_text("Caixa")

        if "CAIXA ECONÔMICA FEDERAL" in value.upper():
            return CaixaInterpreter._extract_text("Caixa")

        return CaixaInterpreter._extract_text(value)
