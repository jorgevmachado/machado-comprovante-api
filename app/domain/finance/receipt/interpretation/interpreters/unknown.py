from __future__ import annotations

from app.domain.finance.receipt.interpretation.interpreters.base import BaseInterpreter
from app.domain.finance.receipt.interpretation.schema import ExtractedField


class UnknownInterpreter(BaseInterpreter):
    @staticmethod
    def _extract_source_institution(text: str) -> ExtractedField[str]:
        return UnknownInterpreter._extract_text("Unknown")
