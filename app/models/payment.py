from __future__ import annotations

from datetime import datetime, date
from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import default_lazy, table_registry
from app.models import utcnow

if TYPE_CHECKING:
    from app.models import User
    from app.models.beneficiary import Beneficiary
    from app.models.institution import Institution


@table_registry.mapped_as_dataclass
class Payment:
    __tablename__ = "payments"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship(
        init=False,
        lazy=default_lazy,
        back_populates="payments",
    )

    receipt_id: Mapped[UUID] = mapped_column(ForeignKey("receipts.id"), nullable=False)
    beneficiary_id: Mapped[UUID] = mapped_column(
        ForeignKey("beneficiaries.id"), nullable=False
    )

    beneficiary: Mapped["Beneficiary"] = relationship(
        init=False,
        lazy=default_lazy,
        back_populates="payments",
    )

    source_institution_id: Mapped[UUID] = mapped_column(
        ForeignKey("institutions.id"), nullable=False
    )

    source_institution: Mapped["Institution"] = relationship(
        init=False,
        lazy=default_lazy,
        foreign_keys=[source_institution_id],
        back_populates="source_payments",
    )

    # Required fields (no defaults) — must come first in __init__
    payment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    destination_institution_id: Mapped[UUID] = mapped_column(
        ForeignKey("institutions.id"), nullable=True
    )

    destination_institution: Mapped["Institution | None"] = relationship(
        init=False,
        lazy=default_lazy,
        foreign_keys=[destination_institution_id],
        back_populates="destination_payments",
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    # Auto-generated / server-managed — excluded from __init__
    id: Mapped[UUID] = mapped_column(
        primary_key=True, default_factory=uuid4, init=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default_factory=utcnow, init=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, init=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, init=False
    )
