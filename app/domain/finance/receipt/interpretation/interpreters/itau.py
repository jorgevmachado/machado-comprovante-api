from __future__ import annotations

import re

from app.domain.finance.receipt.interpretation.interpreters.base import BaseInterpreter
from app.domain.finance.receipt.interpretation.schema import ExtractedField


class ItauInterpreter(BaseInterpreter):
    @staticmethod
    def _extract_authentication(
        text: str,
    ) -> ExtractedField[str]:
        match = re.search(
            r"Autenticação(?: digital Itaú)?:\s*([A-Za-z0-9]+)", text, re.IGNORECASE
        )

        if not match:
            return ItauInterpreter._not_found()
        return ItauInterpreter._extract_text(match.group(1))

    @staticmethod
    def _extract_source_institution(
        text: str,
    ) -> ExtractedField[str]:
        return ItauInterpreter._find_institution(
            text,
            "Itaú",
            ("ITAU UNIBANCO", "ITAÚ UNIBANCO", "AUTENTICAÇÃO DIGITAL ITAÚ"),
        )
