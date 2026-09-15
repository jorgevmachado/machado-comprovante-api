from pydantic import BaseModel
from uuid import UUID


class BeneficiarySchema(BaseModel):
    id: UUID
    name: str
