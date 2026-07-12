import os
from openai import AsyncOpenAI
from src.domain.interfaces import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    OpenAI-backed implementation of LLMProvider.
    Fetches API key from parameters or OPENAI_API_KEY environment variable.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 30.0
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        self.model = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        self.client = AsyncOpenAI(api_key=self.api_key, timeout=timeout)

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Queries OpenAI Async ChatCompletion API to get description.
        Returns the raw string output in JSON format.
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        if content is None:
            return ""
        return content
