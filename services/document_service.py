import uuid

import cloudinary.exceptions
from fastapi import HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from repositories.document_repository import create_document, create_user_document
from schemas.document_upload_response import DocumentUploadResponse
from storage import cloudinary_storage

ALLOWED_CONTENT_TYPES = {"application/pdf"}


def _delete_stored_file(public_id: str) -> None:
    # Best-effort cleanup: an orphaned file in Cloudinary is harmless,
    # so a cleanup failure must not mask the original error.
    try:
        cloudinary_storage.delete_file(public_id)
    except cloudinary.exceptions.Error:
        pass


async def process_document(db: Session, file: UploadFile, user_id: uuid.UUID):

    if (
        not file.filename
        or not file.filename.lower().endswith(".pdf")
        or file.content_type not in ALLOWED_CONTENT_TYPES
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    # Upload to Cloudinary; the SDK is blocking, so run it in a thread
    try:
        uploaded = await run_in_threadpool(
            cloudinary_storage.upload_file,
            file.file,
            file.filename,
        )
    except cloudinary.exceptions.Error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="File storage is unavailable, please try again later",
        ) from None

    try:
        document = create_document(
            db=db,
            filename=file.filename,
        )

        create_user_document(
            db=db,
            user_id=user_id,
            document_id=document.id,
        )

        db.commit()
        db.refresh(document)
    except SQLAlchemyError:
        db.rollback()
        _delete_stored_file(uploaded["public_id"])

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save the uploaded document",
        ) from None

    return DocumentUploadResponse(
        message="Document uploaded successfully",
        document_id=document.id,
        filename=document.file_name,
        status="uploaded",
    )
