# ============================================================
# Resume Text Extractor — PDF / DOCX / TXT
# ============================================================
import os
from backend.core.logger import get_logger

log = get_logger("extractor")


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from PDF file."""
    try:
        import PyPDF2
        text = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        log.error(f"PDF extraction error: {e}")
        return ""


def extract_text_from_docx(filepath: str) -> str:
    """Extract text from DOCX file."""
    try:
        import docx
        doc = docx.Document(filepath)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return text.strip()
    except Exception as e:
        log.error(f"DOCX extraction error: {e}")
        return ""


def extract_text(filepath: str) -> str:
    """Extract text from resume file based on extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(filepath)
    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    else:
        log.warning(f"Unsupported file type: {ext}")
        return ""
