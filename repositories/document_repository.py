import uuid

from sqlalchemy.orm import Session

from models.documents import Documents
from models.document_chunks import DocumentChunks
from models.user_documents import UserDocuments
from models.document_sections import DocumentSections


def create_document(
    db: Session,
    filename: str,
    storage_public_id: str,
    file_url: str,
    status: str = "processing",
):
    document = Documents(
        file_name=filename,
        storage_public_id=storage_public_id,
        file_url=file_url,
        status=status,
    )

    db.add(document)
    db.flush()

    return document


def update_document_status(
    db: Session,
    document_id: uuid.UUID,
    status: str,
) -> None:
    doc = db.query(Documents).filter(Documents.id == document_id).first()
    if doc:
        doc.status = status
        db.flush()


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
    page_number: int ,
    section_id: uuid.UUID | None = None
):
    chunk = DocumentChunks(
        document_id=document_id,
        content=content,
        embedding=embedding,
        page_number=page_number,
        section_id=section_id
    )

    db.add(chunk)

    return chunk


def get_documents_by_user(
    db: Session,
    user_id: uuid.UUID
) -> list[Documents]:
    return (
        db.query(Documents)
        .join(UserDocuments, UserDocuments.document_id == Documents.id)
        .filter(
            UserDocuments.user_id == user_id,
        )
        .all()
    )

def create_section(
    db: Session,
    document_id: uuid.UUID,
    section_name: str | None,
    content: str,
):
    section = DocumentSections(
        document_id=document_id,
        section_name=section_name,
        content=content,
    )

    db.add(section)
    db.flush()

    return section