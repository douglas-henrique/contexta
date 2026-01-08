"""
Base interface for document loaders.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class DocumentLoader(ABC):
    """Abstract base class for document loaders."""

    @abstractmethod
    async def load(self, file_path: str) -> str:
        """
        Load document content from file path.

        Args:
            file_path: Path to the document file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        pass

    @abstractmethod
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from document.

        Args:
            file_path: Path to the document file

        Returns:
            Dictionary with metadata (title, author, etc.)
        """
        pass

    @abstractmethod
    def supports(self, file_type: str) -> bool:
        """
        Check if this loader supports the given file type.

        Args:
            file_type: File extension or MIME type

        Returns:
            True if supported, False otherwise
        """
        pass
