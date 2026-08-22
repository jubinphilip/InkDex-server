from uuid import UUID
from pydantic import BaseModel


class Question(BaseModel):
    text: str
    document_id: UUID | None = None
