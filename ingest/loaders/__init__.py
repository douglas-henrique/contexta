"""
Document loaders for various file formats.
"""

from pathlib import Path
from typing import Optional

from .base import DocumentLoader
from .docx import DOCXLoader
from .pdf import load_pdf
from .txt import TXTLoader

__all__ = [
    "DocumentLoader",
    "load_pdf",
    "TXTLoader",
    "DOCXLoader",
    "get_loader",
    "load_document",
]


def _detect_file_type(file_path: str) -> str:
    """Detect file type from extension."""
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        return "pdf"
    elif extension in [".txt", ".text"]:
        return "txt"
    elif extension == ".docx":
        return "docx"
    else:
        raise ValueError(f"Unsupported file type: {extension}")


def get_loader(file_path: str) -> str:
    """
    Get the appropriate loader type for a file.

    Args:
        file_path: Path to the file

    Returns:
        File type string ('pdf', 'txt', 'docx')
    """
    return _detect_file_type(file_path)


def load_document(file_path: str, file_type: Optional[str] = None) -> str:
    """
    Load document content using the appropriate loader.

    Args:
        file_path: Path to the document file
        file_type: Optional file type (auto-detected if not provided)

    Returns:
        Extracted text content
    """
    if file_type is None:
        file_type = _detect_file_type(file_path)

    if file_type == "pdf":
        return load_pdf(file_path)
    elif file_type == "txt":
        _ = TXTLoader()  # noqa: F841
        # TXTLoader has async load, but we need sync for now
        # Create a simple sync wrapper
        from pathlib import Path

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        encodings = ["utf-8", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        raise ValueError(f"Could not decode file: {file_path}")
    elif file_type == "docx":
        raise NotImplementedError("DOCX loading not yet implemented")
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
