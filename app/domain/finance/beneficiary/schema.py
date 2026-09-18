from pydantic import BaseModel, ConfigDict
from uuid import UUID


class BeneficiarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
