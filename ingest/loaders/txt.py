"""
Plain text document loader.
"""

from pathlib import Path
from typing import Any, Dict

from .base import DocumentLoader


class TXTLoader(DocumentLoader):
    """Loader for plain text documents."""

    async def load(self, file_path: str) -> str:
        """
        Load text content from file.

        Args:
            file_path: Path to text file

        Returns:
            File content as string
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Try different encodings
        encodings = ["utf-8", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        raise ValueError(f"Could not decode file: {file_path}")

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from text file.

        Args:
            file_path: Path to text file

        Returns:
            Dictionary with file metadata
        """
        path = Path(file_path)
        stat = path.stat()

        return {
            "title": path.stem,
            "file_size": stat.st_size,
            "modified_at": stat.st_mtime,
        }

    def supports(self, file_type: str) -> bool:
        """Check if file type is plain text."""
        return file_type.lower() in ["txt", "text", "text/plain"]
