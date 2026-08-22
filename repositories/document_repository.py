import uuid

from sqlalchemy.orm import Session

from models.documents import Documents
from models.document_chunks import DocumentChunks
from models.user_documents import UserDocuments


def create_document(
    db: Session,
    filename: str,
    storage_public_id: str = "pending",
    file_url: str = "pending"
):
    document = Documents(
        file_name=filename,
        storage_public_id=storage_public_id,
        file_url=file_url
    )

    db.add(document)
    db.flush()

    return document


def update_document_storage_info(
    db: Session,
    document_id: uuid.UUID,
    storage_public_id: str,
    file_url: str
) -> Documents:
    document = db.query(Documents).filter(Documents.id == document_id).first()
    if document:
        document.storage_public_id = storage_public_id
        document.file_url = file_url
        db.flush()
    return document


def get_document_owned_by_user(
    db: Session,
    document_id: uuid.UUID,
    user_id: uuid.UUID
) -> Documents | None:
    return (
        db.query(Documents)
        .join(UserDocuments, UserDocuments.document_id == Documents.id)
        .filter(
            Documents.id == document_id,
            UserDocuments.user_id == user_id,
        )
        .first()
    )


def delete_document(db: Session, document: Documents) -> None:
    db.delete(document)


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
    document_id: uuid.UUID,
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