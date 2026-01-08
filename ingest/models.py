"""
Data models for ingest service.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class DocumentMetadata:
    """Metadata for a document being ingested."""
    document_id: int
    tenant_id: int
    file_path: str
    file_type: str
    title: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class Chunk:
    """Represents a chunk of text with metadata."""
    text: str
    chunk_id: str
    document_id: int
    tenant_id: int
    metadata: Dict[str, Any]
    start_index: Optional[int] = None
    end_index: Optional[int] = None
