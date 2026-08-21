from uuid import UUID

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    message: str
    document_id: UUID
    filename: str
    status: str
