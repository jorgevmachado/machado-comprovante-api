from datetime import datetime

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class BeneficiarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

class BeneficiaryPersistSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str