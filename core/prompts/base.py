"""
Base prompt builder interface.
"""

from abc import ABC, abstractmethod


class PromptBuilder(ABC):
    """Abstract base class for prompt builders."""

    @abstractmethod
    def build(self, **kwargs) -> str:
        """
        Build a prompt from provided context.

        Args:
            **kwargs: Context data for prompt construction

        Returns:
            Formatted prompt string
        """
        pass
