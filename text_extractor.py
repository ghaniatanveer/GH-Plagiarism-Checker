from __future__ import annotations

from io import BytesIO

from PyPDF2 import PdfReader
from docx import Document

from .utils import clean_text

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_text_from_file(filename: str, content: bytes) -> str:
    ext = "." + filename.lower().split(".")[-1] if "." in filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file type. Upload PDF, DOCX, or TXT.")
    if ext == ".pdf":
        return extract_pdf_text(content)
    if ext == ".docx":
        return extract_docx_text(content)
    return clean_text(content.decode("utf-8", errors="ignore"))


def extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    return clean_text(" ".join([(page.extract_text() or "") for page in reader.pages]))


def extract_docx_text(content: bytes) -> str:
    doc = Document(BytesIO(content))
    return clean_text(" ".join([p.text for p in doc.paragraphs]))
