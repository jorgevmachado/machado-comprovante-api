from __future__ import annotations

from app.core.repository.base import BaseRepository
from app.models import (
    Institution,
)


class InstitutionRepository(BaseRepository[Institution]):
    model = Institution
