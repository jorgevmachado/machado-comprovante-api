from pydantic import BaseModel
from uuid import UUID


class InstitutionSchema(BaseModel):
    id: UUID
    name: str
