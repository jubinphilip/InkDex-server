import uuid

from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from database.database import get_db
from middleware.rate_limit import rate_limit
from schemas.document_delete_response import DocumentDeleteResponse
from schemas.document_upload_response import DocumentUploadResponse
from security.bearer import bearer_scheme
from security.current_user import get_current_user_id
from services import document_service


router = APIRouter(
    prefix="/document",
    tags=["Documents"],
    dependencies=[Depends(bearer_scheme)],
)


@router.post(
    "/upload-document",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit)],
)
async def upload_document(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    user_id: uuid.UUID = Depends(get_current_user_id)
):

    return await document_service.process_document(
        db,
        file,
        user_id
    )


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):

    return await document_service.delete_document(
        db,
        document_id,
        user_id
    )