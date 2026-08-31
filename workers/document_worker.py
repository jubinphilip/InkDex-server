import os
import tempfile
import urllib.request
import urllib.error
import uuid

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from database.database import SessionLocal
from repositories.document_repository import create_chunk
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


# Loaded once at worker startup; CPU because the Render worker
# has no access to Apple's MPS device.
try:
    model = SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu",
    )
except Exception:
    logger.error(
        "Failed to load sentence transformer model",
        exc_info=True,
    )
    raise RuntimeError("Embedding model initialization failed")


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
            chunk_size=500,
            chunk_overlap=100,
        )

        chunks_with_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            for chunk in splitter.split_text(text):
                chunks_with_pages.append((chunk, page_number))

        if not chunks_with_pages:
            raise ValueError("No text could be extracted from document")

        chunk_texts = [chunk for chunk, _ in chunks_with_pages]

        embeddings = model.encode(chunk_texts)

        for (chunk, page_number), embedding in zip(
            chunks_with_pages,
            embeddings,
        ):
            create_chunk(
                db=db,
                document_id=doc_uuid,
                content=chunk,
                embedding=embedding.tolist(),
                page_number=page_number,
            )

        db.commit()

        logger.info(f"Document {document_id} processed successfully")

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
