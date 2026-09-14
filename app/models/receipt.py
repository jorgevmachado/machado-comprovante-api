from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4
from typing import TYPE_CHECKING

from sqlalchemy import DateTime,Enum as SAEnum, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import table_registry, default_lazy
from app.models import utcnow
from app.models.enums import ProcessingStatusEnum
if TYPE_CHECKING:
    from app.models.payment import Payment

@table_registry.mapped_as_dataclass
class Receipt:
    __tablename__ = "receipts"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Required fields (no defaults) — must come first in __init__
    file_reference: Mapped[str] = mapped_column(String, nullable=False)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)

    processing_status: Mapped[ProcessingStatusEnum] = mapped_column(
        SAEnum(ProcessingStatusEnum, name="processingstatusenum"),
        nullable=False
    )

    extracted_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default_factory=utcnow, init=False
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

    payment: Mapped["Payment"] = relationship(
        init=False,
        lazy=default_lazy,
        back_populates="receipt"
    )
