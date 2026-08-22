import logging
import os
import tempfile
import urllib.request
import urllib.error
import uuid

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database.database import SessionLocal
from storage import cloudinary_storage
from repositories.document_repository import create_chunk, update_document_storage_info

from utils.logging_config import setup_logger

logger = setup_logger(__name__)

# Load the sentence transformer model once at the module level for the worker to avoid repetitive model initialization it is declared globally.

try:
    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
except Exception as e:
    logger.error("Failed to load sentence transformer model", exc_info=True)
    raise RuntimeError("Embedding model initialization failed") from e


def process_document(document_id: str, file_path: str) -> None:
    db: Session = SessionLocal()

    try:
        # Resolve target document UUID
        doc_uuid = document_id if isinstance(document_id, uuid.UUID) else uuid.UUID(document_id)

        # Upload file to Cloudinary from local temp path
        try:
            with open(file_path, "rb") as f:
                uploaded = cloudinary_storage.upload_file(f, os.path.basename(file_path))
        except Exception as e:
            logger.error(f"Failed to upload document {document_id} to Cloudinary", exc_info=True)
            raise RuntimeError("Cloudinary upload failed") from e

        # Update the document storage metadata in the database
        try:
            update_document_storage_info(
                db=db,
                document_id=doc_uuid,
                storage_public_id=uploaded["public_id"],
                file_url=uploaded["url"]
            )
        except SQLAlchemyError as e:
            logger.error(f"Failed to update document storage info for {document_id}", exc_info=True)
            # Try to delete the uploaded Cloudinary file since database sync failed
            try:
                cloudinary_storage.delete_file(uploaded["public_id"])
            except Exception:
                pass
            raise


        try:
            reader = PdfReader(file_path)
        except Exception as e:
            logger.error(f"Failed to parse PDF file from path: {file_path}", exc_info=True)
            raise ValueError("Invalid PDF format") from e

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )

        chunks_with_pages = []

        # Extract and chunk PDF
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            chunks = splitter.split_text(text)
            for chunk in chunks:
                chunks_with_pages.append((chunk, page_number))

        if not chunks_with_pages:
            raise ValueError("No text could be extracted from document")

        # Extract only text for embedding
        chunk_texts = [chunk for chunk, _ in chunks_with_pages]

        # Generate embeddings
        embeddings = model.encode(chunk_texts)

        # Save chunks and  embeddings
        for (chunk, page_number), embedding in zip(chunks_with_pages, embeddings):
            create_chunk(
                db=db,
                document_id=doc_uuid,
                content=chunk,
                embedding=embedding.tolist(),
                page_number=page_number
            )

        db.commit()

    except (SQLAlchemyError, ValueError, RuntimeError) as e:
        db.rollback()
        logger.error(f"Processing failed for document {document_id}: {e}", exc_info=True)
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error processing document {document_id}: {e}", exc_info=True)
        raise

    finally:
        db.close()
        # Clean up temporary local file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
