import os
import tempfile
import urllib.request
import urllib.error
import uuid
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session
from config.embeddings import embedding_model
from database.database import SessionLocal
from repositories.document_repository import create_chunk, update_document_status
from utils.logging_config import setup_logger
from utils.ocr import ocr_page
from utils.section_detector import split_into_sections

logger = setup_logger(__name__)


def process_document(
    document_id: str,
    file_url: str,
) -> None:

    db: Session = SessionLocal()
    temp_file_path = None

    try:
        doc_uuid = (
            document_id
            if isinstance(document_id, uuid.UUID)
            else uuid.UUID(document_id)
        )

        # Download the PDF from Cloudinary to a temporary local file
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False,
            ) as temp_file:
                temp_file_path = temp_file.name

            urllib.request.urlretrieve(file_url, temp_file_path)

        except (urllib.error.URLError, OSError) as e:
            logger.error(
                f"Failed to download document {document_id} from Cloudinary",
                exc_info=True,
            )
            raise RuntimeError("Failed to download document") from e

        try:
            reader = PdfReader(temp_file_path)
        except Exception as e:
            logger.error(
                f"Failed to parse PDF file: {temp_file_path}",
                exc_info=True,
            )
            raise ValueError("Invalid PDF format") from e

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

        chunks_with_pages = []
        current_section = None

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                text = ocr_page(temp_file_path, page_number)

            sections, current_section = split_into_sections(
                text,
                current_section,
            )

            for section_text, section_name in sections:
                for chunk in splitter.split_text(section_text):
                    chunks_with_pages.append(
                        (chunk, page_number, section_name)
                    )

        if not chunks_with_pages:
            raise ValueError("No text could be extracted from document")

        chunk_texts = [chunk for chunk, _, _ in chunks_with_pages]

        embeddings = embedding_model.encode(chunk_texts)

        for (
            chunk,page_number,section_name,), embedding in zip(
            chunks_with_pages,
            embeddings,
        ):
            create_chunk(
                db=db,
                document_id=doc_uuid,
                content=chunk,
                embedding=embedding.tolist(),
                page_number=page_number,
                section_name=section_name,
            )

        update_document_status(db, doc_uuid, "completed")
        db.commit()

        logger.info(f"Document {document_id} processed successfully")

    except Exception:
        db.rollback()
        try:
            update_document_status(db, doc_uuid, "failed")
            db.commit()
        except Exception:
            db.rollback()

        logger.error(
            f"Processing failed for document {document_id}",
            exc_info=True,
        )
        raise

    finally:
        db.close()

        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                logger.warning(
                    f"Failed to remove temporary file {temp_file_path}",
                    exc_info=True,
                )
