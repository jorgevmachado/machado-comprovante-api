from __future__ import annotations

from app.core.repository.base import BaseRepository
from app.models import (
    Payment,
)


class PaymentRepository(BaseRepository[Payment]):
    model = Payment
