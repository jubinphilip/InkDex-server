import uuid

import cloudinary.exceptions
from fastapi import HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from repositories.document_repository import (
    create_document,
    create_user_document,
    delete_document as delete_document_record,
    get_document_owned_by_user,
)
from schemas.document_delete_response import DocumentDeleteResponse
from schemas.document_upload_response import DocumentUploadResponse
from storage import cloudinary_storage
from queues.queue import document_queue
from rq import Retry
from utils.logging_config import setup_logger

import os
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

logger = setup_logger(__name__)

ALLOWED_CONTENT_TYPES = {"application/pdf"}


def _delete_stored_file(public_id: str) -> None:
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

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    stored_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    # Save uploaded PDF to local disk
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

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

        # Enqueue background processing job in Redis queue with the local path
        document_queue.enqueue(
            "workers.document_worker.process_document",
            str(document.id),
            file_path,
            retry=Retry(max=3)
        )
    except SQLAlchemyError as e:
        db.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Failed to create document record for upload: {file.filename}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save the uploaded document",
        ) from None

    return DocumentUploadResponse(
        message="Document uploaded and processing started",
        document_id=document.id,
        filename=document.file_name,
        status="processing",
    )


async def delete_document(db: Session, document_id: uuid.UUID, user_id: uuid.UUID):

    document = get_document_owned_by_user(
        db=db,
        document_id=document_id,
        user_id=user_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    storage_public_id = document.storage_public_id

    try:
        delete_document_record(db, document)
        db.commit()
    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete the document",
        ) from None

    # Remove the file from Cloudinary only after the DB delete is committed
    await run_in_threadpool(_delete_stored_file, storage_public_id)

    return DocumentDeleteResponse(
        message="Document deleted successfully",
        document_id=document_id,
    )
