from __future__ import annotations

from app.core.repository.base import BaseRepository
from app.models import (
    Receipt,
)


class ReceiptRepository(BaseRepository[Receipt]):
    model = Receipt
