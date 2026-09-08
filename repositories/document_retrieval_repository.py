import uuid
from sqlalchemy.orm import Session
from models.document_chunks import DocumentChunks
from models.user_documents import UserDocuments
from models.document_sections import DocumentSections


def get_similar_chunks(
    db: Session,
    query_embedding: list[float],
    user_id: uuid.UUID,
    document_id: uuid.UUID | None,
    top_k: int,
    distance_threshold: float,
):
    # Calculate cosine distance using pgvector
    distance_expr = DocumentChunks.embedding.cosine_distance(query_embedding).label("distance")

    #Take answer from documents only uploaded by specific user
    query = (
        db.query(
            DocumentChunks,
            DocumentSections,
            distance_expr,
        )
        .join(
            DocumentSections,
            DocumentSections.id == DocumentChunks.section_id,
        )
        .join(
            UserDocuments,
            UserDocuments.document_id == DocumentChunks.document_id,
        )
        .filter(UserDocuments.user_id == user_id)
    )

    if document_id is not None:
        query = query.filter(DocumentChunks.document_id == document_id)

    # Filter chunks within the similarity threshold
    query = query.filter(distance_expr <= distance_threshold)

    query = query.order_by(distance_expr.asc())

    return query.limit(top_k).all()


def get_section_chunks(
    db: Session,
    section_id: uuid.UUID,
    document_id: uuid.UUID,
):
    return (
        db.query(DocumentChunks)
        .filter(
            DocumentChunks.section_id == section_id,
            DocumentChunks.document_id == document_id,
        )
        .order_by(DocumentChunks.page_number.asc())
        .all()
    )