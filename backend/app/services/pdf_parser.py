import logging
import fitz  # PyMuPDF
import pymupdf4llm

logger = logging.getLogger(__name__)

def parse_pdf_to_markdown(file_path: str) -> str:
    """
    Parses a PDF file into Markdown format using pymupdf4llm.
    Falls back to raw text extraction via PyMuPDF if an error occurs.
    """
    try:
        # Use pymupdf4llm to extract text in markdown format
        md_text = pymupdf4llm.to_markdown(file_path)
        return md_text
    except Exception as e:
        logger.error(f"Error parsing PDF to markdown using pymupdf4llm: {e}")
        logger.info("Falling back to raw text extraction via PyMuPDF.")
        try:
            # Fallback to PyMuPDF raw text extraction
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n\n"
            return text
        except Exception as fallback_e:
            logger.error(f"Error during fallback PDF parsing: {fallback_e}")
            raise Exception(f"Failed to parse PDF: {e} | Fallback failed: {fallback_e}")
