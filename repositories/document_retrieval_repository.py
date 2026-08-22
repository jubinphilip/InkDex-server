import uuid
from sqlalchemy.orm import Session
from models.document_chunks import DocumentChunks
from models.user_documents import UserDocuments


def get_similar_chunks(
    db: Session,
    query_embedding: list[float],
    user_id: uuid.UUID,
    document_id: uuid.UUID | None = None,
    top_k: int = 5,
    distance_threshold: float = 0.50
):
    # Calculate cosine distance using pgvector
    distance_expr = DocumentChunks.embedding.cosine_distance(query_embedding).label("distance")

    #Take answer from documents only uploaded by specific user
    query = (
        db.query(DocumentChunks, distance_expr)
        .join(UserDocuments, UserDocuments.document_id == DocumentChunks.document_id)
        .filter(UserDocuments.user_id == user_id)
    )

    if document_id is not None:
        query = query.filter(DocumentChunks.document_id == document_id)

    # Filter chunks within the similarity threshold
    query = query.filter(distance_expr <= distance_threshold)

    query = query.order_by(distance_expr.asc())

    return query.limit(top_k).all()

