import pytest
from src.application.services import AnalysisService, AnalysisException
from src.application.prompt_builder import PromptBuilder
from src.application.response_parser import AnalysisResultParser # AnalysisResultParser 명칭으로 임포트
from src.domain.models import AnalyzeRequest, TestType, ChoiceLabel, AnalysisResult
from tests.unit.test_llm_provider import FakeLLMProvider

@pytest.fixture
def sample_request():
    return AnalyzeRequest(
        test_type=TestType.RC,
        part=5,
        question_text="The company's ------- to the new market was successful.",
        choices={"A": "expand", "B": "expansion", "C": "expansive", "D": "expansively"},
        correct_answer=ChoiceLabel.B,
        user_answer=ChoiceLabel.C
    )

@pytest.fixture
def mock_ai_response():
    return """
    {
      "translation": {
        "question": "그 회사의 새로운 시장으로의 -------은/는 성공적이었다.",
        "choices": {
          "A": "확장하다 (동사 원형)",
          "B": "확장 (명사)",
          "C": "확장적인 (형용사)",
          "D": "확장적으로 (부사)"
        }
      },
      "correctAnswer": {
        "choice": "B",
        "text": "expansion"
      },
      "correctReason": {
        "summary": "소유격 뒤 명사 필요",
        "detail": "소유격 뒤에 명사가 와야 합니다.",
        "grammarRule": "소유격 + 명사"
      },
      "wrongAnswerReason": {
        "selectedChoice": "C",
        "selectedText": "expansive",
        "summary": "형용사는 이 위치에서 주어 역할을 할 수 없음",
        "detail": "형용사는 이 위치에서 주어 역할을 할 수 없습니다."
      },
      "errorCategory": {
        "primary": "PART_OF_SPEECH",
        "secondary": null,
        "description": "품사 판별 오류입니다."
      },
      "learningPoint": {
        "title": "소유격 뒤 품사 판별법",
        "explanation": "핵심 개념 설명입니다.",
        "examples": [
          {
            "english": "Her dedication to the project impressed everyone.",
            "korean": "그녀의 프로젝트에 대한 헌신은 모두에게 감동을 주었다."
          },
          {
            "english": "The manager's approval is required before proceeding.",
            "korean": "진행하기 전에 관리자의 승인이 필요합니다."
          }
        ],
        "tip": "소유격 뒤 + 빈칸 + 전치사/동사 → 빈칸은 100% 명사!"
      },
      "vocabulary": [
        {
          "word": "expansion",
          "partOfSpeech": "noun",
          "meaning": "확장, 확대",
          "exampleSentence": "The expansion of the business into Asia was a strategic decision."
        }
      ],
      "confidence": {
        "score": 0.95,
        "reason": "명확함"
      },
      "disclaimer": "이 분석은 AI가 생성한 것으로, 실제 출제 의도와 다를 수 있습니다. 참고 자료로 활용하시고, 정확한 해설은 공식 교재를 확인하세요."
    }
    """

@pytest.mark.asyncio
async def test_analysis_service_success(sample_request, mock_ai_response):
    """정상적인 흐름에서 Service가 prompt_builder, llm_provider, AnalysisResultParser를 사용해 AnalysisResult 결과를 리턴하는지 검증"""
    fake_llm = FakeLLMProvider(mock_ai_response)
    builder = PromptBuilder()
    parser = AnalysisResultParser()  # AnalysisResultParser 사용
    
    service = AnalysisService(
        prompt_builder=builder,
        llm_provider=fake_llm,
        response_parser=parser
    )
    
    result = await service.analyze(sample_request)
    
    assert isinstance(result, AnalysisResult)
    assert result.translation.question == "그 회사의 새로운 시장으로의 -------은/는 성공적이었다."
    assert result.error_category.primary.value == "PART_OF_SPEECH"

@pytest.mark.asyncio
async def test_analysis_service_llm_failure(sample_request):
    """LLM Provider 내부 호출 실패 시 AnalysisException 예외가 성립하는지 검증"""
    class FailLLMProvider(FakeLLMProvider):
        async def generate(self, system_prompt: str, user_prompt: str) -> str:
            raise RuntimeError("API Timeout / OpenAI Server Error")

    service = AnalysisService(
        prompt_builder=PromptBuilder(),
        llm_provider=FailLLMProvider(),
        response_parser=AnalysisResultParser() # AnalysisResultParser 사용
    )
    
    with pytest.raises(AnalysisException) as excinfo:
        await service.analyze(sample_request)
        
    assert "AI analysis failed" in str(excinfo.value)
    assert "API Timeout" in str(excinfo.value)

@pytest.mark.asyncio
async def test_analysis_service_parse_failure(sample_request):
    """AI 응답 파싱 실패 시 AnalysisException 예외 처리 검증"""
    fake_llm = FakeLLMProvider("{'invalid_json_format':")
    
    service = AnalysisService(
        prompt_builder=PromptBuilder(),
        llm_provider=fake_llm,
        response_parser=AnalysisResultParser() # AnalysisResultParser 사용
    )
    
    with pytest.raises(AnalysisException) as excinfo:
        await service.analyze(sample_request)
        
    assert "AI response parsing failed" in str(excinfo.value)
