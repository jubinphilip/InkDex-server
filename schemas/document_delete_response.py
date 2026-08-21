from uuid import UUID

from pydantic import BaseModel


class DocumentDeleteResponse(BaseModel):
    message: str
    document_id: UUID
