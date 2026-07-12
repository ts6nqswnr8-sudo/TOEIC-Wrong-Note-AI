import json
import re
from pydantic import ValidationError
from src.domain.models import AnalysisResult


class ResponseParseException(Exception):
    """Exception raised when parsing AI responses fails."""
    pass


class ResponseParser:
    def __init__(self) -> None:
        pass

    def parse(self, raw_response: str) -> AnalysisResult:
        """
        Parses the raw string response from LLM, strips markdown code blocks,
        and converts it safely into an AnalysisResult domain model.
        Throws ResponseParseException if JSON parsing or Pydantic validation fails.
        """
        # 1. 마크다운 코드 블록(```json ... ``` 또는 ``` ... ```) 제거를 위한 전처리
        cleaned_text = raw_response.strip()
        pattern = r"^```(?:json)?\s*(.*?)\s*```$"
        match = re.match(pattern, cleaned_text, re.DOTALL)
        if match:
            cleaned_text = match.group(1).strip()

        # 2. JSON 파싱 시도
        try:
            parsed_json = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            raise ResponseParseException(f"Invalid JSON format: {str(e)}") from e

        # 3. Pydantic validation 적용하여 AnalysisResult로 매핑
        try:
            result = AnalysisResult.model_validate(parsed_json)
            return result
        except ValidationError as e:
            raise ResponseParseException(f"Validation failed for AnalysisResult: {str(e)}") from e
