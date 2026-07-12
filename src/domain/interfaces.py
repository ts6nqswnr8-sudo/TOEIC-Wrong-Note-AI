from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.domain.models import AnalysisResult


class LLMProvider(ABC):
    """
    Abstract Interface for LLM provider.
    Ensures that domain and application layers do not directly depend on external LLM SDKs (e.g. OpenAI).
    """

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Sends the system and user prompts to the LLM agent and returns the raw string response.
        """
        pass


class NoteRepository(ABC):
    """
    Abstract Interface for wrong note repository.
    Isolates domain logic from concrete database technologies.
    """

    @abstractmethod
    async def save(self, note: AnalysisResult) -> AnalysisResult:
        """
        Saves a wrong note (AnalysisResult) to the database.
        """
        pass

    @abstractmethod
    async def find_all(self) -> List[AnalysisResult]:
        """
        Retrieves all wrong notes from the database.
        """
        pass

    @abstractmethod
    async def find_by_id(self, note_id: UUID) -> Optional[AnalysisResult]:
        """
        Retrieves a single wrong note by its unique ID.
        """
        pass

    @abstractmethod
    async def delete(self, note_id: UUID) -> bool:
        """
        Deletes a wrong note from the database. Returns True if deleted, False otherwise.
        """
        pass
