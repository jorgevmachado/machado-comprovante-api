from app.domain.finance.receipt.interpretation.institutions.rules.caixa import (
    CaixaRules,
)
from app.domain.finance.receipt.interpretation.institutions.rules.itau import ItauRules
from app.domain.finance.receipt.interpretation.institutions.rules.nubank import (
    NubankRules,
)

INSTITUTION_RULES = (
    *NubankRules.rules(),
    *ItauRules.rules(),
    *CaixaRules.rules(),
)
