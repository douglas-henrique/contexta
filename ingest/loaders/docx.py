"""
DOCX document loader.
"""

from typing import Any, Dict

from .base import DocumentLoader


class DOCXLoader(DocumentLoader):
    """Loader for DOCX documents."""

    async def load(self, file_path: str) -> str:
        """
        Load text content from DOCX file.

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text content
        """
        # TODO: Implement DOCX loading using python-docx
        # For now, raise NotImplementedError
        raise NotImplementedError("DOCX loading not yet implemented")

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from DOCX.

        Args:
            file_path: Path to DOCX file

        Returns:
            Dictionary with DOCX metadata
        """
        # TODO: Extract DOCX metadata (title, author, etc.)
        raise NotImplementedError("DOCX metadata extraction not yet implemented")

    def supports(self, file_type: str) -> bool:
        """Check if file type is DOCX."""
        return file_type.lower() in [
            "docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
