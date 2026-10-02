from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, BaseModel


class CategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None