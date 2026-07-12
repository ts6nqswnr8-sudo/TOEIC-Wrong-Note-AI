from src.application.prompt_builder import PromptBuilder
from src.application.response_parser import ResponseParser, ResponseParseException
from src.domain.interfaces import LLMProvider
from src.domain.models import AnalyzeRequest, AnalysisResult


class AnalysisException(Exception):
    """Exception raised when the high-level wrong note analysis fails."""
    pass


class AnalysisService:
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm_provider: LLMProvider,
        response_parser: ResponseParser
    ) -> None:
        self.prompt_builder = prompt_builder
        self.llm_provider = llm_provider
        self.response_parser = response_parser

    async def analyze(self, request: AnalyzeRequest) -> AnalysisResult:
        """
        Runs the core wrong note analysis pipeline:
        AnalyzeRequest -> PromptBuilder -> LLMProvider -> ResponseParser -> AnalysisResult
        """
        # 1. 프롬프트 생성
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_user_prompt(request)

        # 2. LLM 호출 및 결과 수신
        try:
            raw_response = await self.llm_provider.generate(system_prompt, user_prompt)
        except Exception as e:
            raise AnalysisException(f"AI analysis failed to execute: {str(e)}") from e

        # 3. JSON 정제 및 AnalysisResult 도메인 인스턴스화
        try:
            result = self.response_parser.parse(raw_response)
            result.part = request.part
            return result
        except ResponseParseException as e:
            raise AnalysisException(f"AI response parsing failed: {str(e)}") from e
