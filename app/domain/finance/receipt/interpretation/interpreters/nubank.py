from __future__ import annotations

import re
from datetime import date

from app.domain.finance.receipt.interpretation.interpreters.base import BaseInterpreter
from app.domain.finance.receipt.interpretation.schema import ExtractedField


class NubankInterpreter(BaseInterpreter):
    @staticmethod
    def _extract_due_date(text: str) -> ExtractedField[date]:
        match = re.search(
            r"Vencimento\s+(\d{2})\s+([A-Z]{3})\s+(\d{4})",
            text,
            re.IGNORECASE,
        )

        if not match:
            return NubankInterpreter._not_found()
        day, month, year = match.groups()
        months = NubankInterpreter.MONTHS
        month_number = months.get(month.upper())
        if month_number is None:
            return NubankInterpreter._ambiguous()
        try:
            value = date(
                int(year),
                month_number,
                int(day),
            )
        except ValueError:
            return NubankInterpreter._ambiguous()
        return NubankInterpreter._parse_date(f"{value.day}/{value.month}/{value.year}")

    @staticmethod
    def _extract_payment_date(
        text: str,
    ) -> ExtractedField[date]:
        match = re.search(
            r"(\d{2})\s+([A-Z]{3})\s+(\d{4})\s*-\s*\d{2}:\d{2}:\d{2}",
            text,
            re.IGNORECASE,
        )
        if not match:
            return NubankInterpreter._not_found()
        day, month, year = match.groups()
        months = NubankInterpreter.MONTHS
        month_number = months.get(month.upper())
        if month_number is None:
            return NubankInterpreter._ambiguous()
        try:
            value = date(int(year), month_number, int(day))
        except ValueError:
            return NubankInterpreter._ambiguous()
        return NubankInterpreter._parse_date(f"{value.day}/{value.month}/{value.year}")

    @staticmethod
    def _extract_source_institution(text: str) -> ExtractedField[str]:
        return NubankInterpreter._find_institution(
            text,
            "Nubank",
            (
                "NU PAGAMENTOS SA",
                "NU PAGAMENTOS S.A.",
                "NUBANK.COM.BR",
            ),
        )
