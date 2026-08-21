import uuid

from sqlalchemy.orm import Session

from models.documents import Documents
from models.document_chunks import DocumentChunks
from models.user_documents import UserDocuments


def create_document(
    db: Session,
    filename: str
):
    document = Documents(
        file_name=filename
    )

    db.add(document)
    db.flush()

    return document


def create_user_document(
    db: Session,
    user_id: uuid.UUID,
    document_id: uuid.UUID
):
    user_document = UserDocuments(
        user_id=user_id,
        document_id=document_id
    )

    db.add(user_document)
    db.flush()

    return user_document


def create_chunk(
    db: Session,
    document_id: int,
    content: str,
    embedding: list[float],
    page_number: int 
):
    chunk = DocumentChunks(
        document_id=document_id,
        content=content,
        embedding=embedding,
        page_number=page_number
    )

    db.add(chunk)

    return chunk