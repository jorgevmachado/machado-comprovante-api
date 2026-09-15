from pydantic import BaseModel
from uuid import UUID
from datetime import date
from decimal import Decimal


class PaymentSchema(BaseModel):
    id: UUID
    payment_date: date
    amount: Decimal
