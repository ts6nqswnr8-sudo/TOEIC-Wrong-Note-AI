from abc import ABC, abstractmethod


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
