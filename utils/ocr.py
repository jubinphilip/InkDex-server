import io

import pymupdf
import pytesseract
from PIL import Image

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def ocr_page(
    file_path: str,
    page_number: int,
) -> str:
    """
    Render a PDF page as an image and extract text using OCR.

    page_number is 1-based.
    """

    try:
        pdf = pymupdf.open(file_path)

        try:
            page_index = page_number - 1

            if page_index < 0 or page_index >= len(pdf):
                raise ValueError(
                    f"Invalid page number: {page_number}"
                )

            page = pdf[page_index]

            # Render page at 2x resolution
            matrix = pymupdf.Matrix(2, 2)
            pix = page.get_pixmap(matrix=matrix)

            # Convert rendered PNG bytes into a PIL Image
            image = Image.open(
                io.BytesIO(pix.tobytes("png"))
            )

            text = pytesseract.image_to_string(
                image,
                config="--psm 6",
            )

            return text.strip()

        finally:
            pdf.close()

    except Exception:
        logger.error(
            f"OCR failed for page {page_number} "
            f"of document {file_path}",
            exc_info=True,
        )
        raise