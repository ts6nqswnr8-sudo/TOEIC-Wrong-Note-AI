import pytest
import json
from src.domain.interfaces import LLMProvider
from src.domain.models import AnalysisResult
from src.infrastructure.fake_llm_provider import FakeLLMProvider as RealFakeLLMProvider


class FakeLLMProvider(LLMProvider):
    """테스트를 위한 Fake LLMProvider 오버라이딩 구현체"""
    def __init__(self, stub_response: str = "{}") -> None:
        self.stub_response = stub_response
        self.last_system_prompt = None
        self.last_user_prompt = None

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.stub_response


@pytest.mark.asyncio
async def test_fake_llm_provider_generate():
    """기존 FakeLLMProvider 스텁 테스트"""
    fake = FakeLLMProvider(stub_response='{"mocked": true}')
    response = await fake.generate("System Rules", "User Input")
    assert response == '{"mocked": true}'
    assert fake.last_system_prompt == "System Rules"
    assert fake.last_user_prompt == "User Input"


@pytest.mark.asyncio
async def test_infrastructure_fake_llm_provider_tdd():
    """TDD로 검증할 FakeLLMProvider 요구사항 테스트 (정상 응답, 호출 횟수, 입력 전달 여부, 동일 입력 동일 응답)"""
    provider = RealFakeLLMProvider()
    
    # 1. 초기 호출 정보 검증
    assert provider.call_count == 0
    assert provider.last_system_prompt is None
    assert provider.last_user_prompt is None
    
    system_prompt = "tutor rules"
    user_prompt = """
[Context Details]
- Test Type: RC
- Part: 5

[Question]
The company's ------- to the new market was successful.

[Choices]
{
  "A": "expand",
  "B": "expansion",
  "C": "expansive",
  "D": "expansively"
}

[Answer Record]
- Correct Answer: B (expansion)
- User's Answer (Wrong): C (expansive)
"""
    
    # 2. 실행 및 응답 파이프라인 검증 (정상 응답 및 입력 전달 여부)
    response_str = await provider.generate(system_prompt, user_prompt)
    assert provider.call_count == 1
    assert provider.last_system_prompt == system_prompt
    assert provider.last_user_prompt == user_prompt
    
    # JSON Parsing 및 스키마 검증
    res_data = json.loads(response_str)
    assert res_data["correctAnswer"]["choice"] == "B"
    assert res_data["correctAnswer"]["text"] == "expansion"
    assert res_data["wrongAnswerReason"]["selectedChoice"] == "C"
    assert res_data["wrongAnswerReason"]["selectedText"] == "expansive"
    
    # Pydantic 도메인 모델 검증
    result_model = AnalysisResult.model_validate(res_data)
    assert result_model.correct_answer.choice == "B"
    assert result_model.wrong_answer_reason.selected_choice == "C"
    
    # fake 응답 식별 데이터 검증 (스펙과 부합)
    assert "fake" in result_model.disclaimer.lower() or "mock" in result_model.disclaimer.lower()
    
    # 3. 동일한 입력에 동일한 응답 반환 검증
    second_response = await provider.generate(system_prompt, user_prompt)
    assert provider.call_count == 2
    assert second_response == response_str
