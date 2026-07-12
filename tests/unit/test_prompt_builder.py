import pytest
from src.application.prompt_builder import PromptBuilder
from src.domain.models import AnalyzeRequest, TestType, ChoiceLabel

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

def test_system_prompt_contains_rules():
    """시스템 프롬프트가 오답 분류 가이드 및 JSON 스키마 요구사항을 포함하는지 검증"""
    builder = PromptBuilder()
    system_prompt = builder.build_system_prompt()
    
    assert "PART_OF_SPEECH" in system_prompt
    assert "translation" in system_prompt
    assert "correctAnswer" in system_prompt
    assert "wrongAnswerReason" in system_prompt
    assert "errorCategory" in system_prompt
    assert "learningPoint" in system_prompt
    assert "vocabulary" in system_prompt

def test_user_prompt_contains_request_details(sample_request):
    """유저 프롬프트가 AnalyzeRequest의 세부 문제 데이터를 형식에 유효하게 주입하는가"""
    builder = PromptBuilder()
    user_prompt = builder.build_user_prompt(sample_request)
    
    # 문제 세부 정보 검증
    assert "5" in user_prompt
    assert "RC" in user_prompt
    assert "The company's ------- to the new market was successful." in user_prompt
    assert "expansion" in user_prompt
    assert "B" in user_prompt
    assert "C" in user_prompt
