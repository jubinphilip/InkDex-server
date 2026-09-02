from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    file_name: str
    file_url: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
