"""
RAG prompt builder for question answering.
"""

from typing import Any, Dict, List

from .base import PromptBuilder


class RAGPromptBuilder(PromptBuilder):
    """
    Prompt builder for RAG-based question answering.

    Constructs prompts that include:
    - Context from retrieved documents
    - User question
    - Instructions for answer generation
    """

    def __init__(
        self,
        system_instruction: str = None,
        context_prefix: str = "Context:",
        question_prefix: str = "Question:",
        answer_prefix: str = "Answer:",
    ):
        """
        Initialize RAG prompt builder.

        Args:
            system_instruction: Optional system-level instruction
            context_prefix: Prefix for context section
            question_prefix: Prefix for question section
            answer_prefix: Prefix for answer section
        """
        self.system_instruction = (
            system_instruction or self._default_system_instruction()
        )
        self.context_prefix = context_prefix
        self.question_prefix = question_prefix
        self.answer_prefix = answer_prefix

    def _default_system_instruction(self) -> str:
        """Default system instruction for RAG."""
        return (
            "You are a helpful assistant that answers questions based on the "
            "provided context. Use only the information from the context to "
            "answer the question. If the context doesn't contain enough "
            "information to answer the question, say so. Be concise and "
            "accurate in your responses."
        )

    def build(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
        max_context_length: int = 3000,
    ) -> str:
        """
        Build RAG prompt with context and question.

        Args:
            question: User's question
            context_chunks: List of context chunks with 'text' and optionally 'score', 'document_id'
            max_context_length: Maximum characters for context section

        Returns:
            Formatted prompt string
        """
        # Build context section from chunks
        context_parts = []
        current_length = 0

        for chunk in context_chunks:
            chunk_text = chunk.get("text", "")
            if current_length + len(chunk_text) > max_context_length:
                break

            context_parts.append(chunk_text)
            current_length += len(chunk_text)

        context = "\n\n".join(context_parts)

        # Build prompt
        prompt_parts = [
            self.system_instruction,
            "",
            f"{self.context_prefix}",
            context,
            "",
            f"{self.question_prefix} {question}",
            "",
            f"{self.answer_prefix}",
        ]

        return "\n".join(prompt_parts)

    def build_with_sources(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
        max_context_length: int = 3000,
        include_sources: bool = True,
    ) -> str:
        """
        Build RAG prompt with context, question, and source citations.

        Args:
            question: User's question
            context_chunks: List of context chunks with metadata
            max_context_length: Maximum characters for context section
            include_sources: Whether to include source information in prompt

        Returns:
            Formatted prompt string
        """
        # Build context with source citations
        context_parts = []
        current_length = 0

        for idx, chunk in enumerate(context_chunks, 1):
            chunk_text = chunk.get("text", "")
            source_info = ""

            if include_sources:
                doc_id = chunk.get("document_id", "unknown")
                chunk_idx = chunk.get("chunk_index", idx)
                source_info = f" [Source: Document {doc_id}, Chunk {chunk_idx}]"

            full_chunk = f"{chunk_text}{source_info}"

            if current_length + len(full_chunk) > max_context_length:
                break

            context_parts.append(full_chunk)
            current_length += len(full_chunk)

        context = "\n\n".join(context_parts)

        # Build prompt
        prompt_parts = [
            self.system_instruction,
            "",
            f"{self.context_prefix}",
            context,
            "",
            f"{self.question_prefix} {question}",
            "",
            f"{self.answer_prefix}",
        ]

        return "\n".join(prompt_parts)
