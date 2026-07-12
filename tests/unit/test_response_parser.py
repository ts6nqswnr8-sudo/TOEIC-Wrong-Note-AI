import pytest
import json
from src.application.response_parser import ResponseParser, ResponseParseException
from src.domain.models import AnalysisResult, ErrorCategoryCode

@pytest.fixture
def valid_json_string():
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

def test_parse_valid_json(valid_json_string):
    """정상적인 JSON 문자열을 AnalysisResult 인스턴스로 변환 성공"""
    parser = ResponseParser()
    result = parser.parse(valid_json_string)
    
    assert isinstance(result, AnalysisResult)
    assert result.translation.question == "그 회사의 새로운 시장으로의 -------은/는 성공적이었다."
    assert result.error_category.primary == ErrorCategoryCode.PART_OF_SPEECH

def test_parse_markdown_json_block(valid_json_string):
    """markdown 형식의 json 코드 블록(```json ... ```)으로 래핑된 문자열도 감지하여 올바르게 변환함"""
    wrapped_str = f"```json\n{valid_json_string}\n```"
    parser = ResponseParser()
    result = parser.parse(wrapped_str)
    
    assert isinstance(result, AnalysisResult)
    assert result.correct_answer.choice == "B"

def test_parse_invalid_json_format_raises_exception():
    """중괄호 누락 등 JSON 자체가 깨진 경우 ResponseParseException 발생"""
    broken_json = '{"translation": { "question": "test"'  # 닫히지 않은 json
    parser = ResponseParser()
    
    with pytest.raises(ResponseParseException) as excinfo:
        parser.parse(broken_json)
    
    assert "Invalid JSON format" in str(excinfo.value)

def test_parse_missing_required_fields_raises_exception():
    """필수 필드가 없는 JSON 전달 시 ResponseParseException 발생"""
    incomplete_json = '{"correctAnswer": {"choice": "B", "text": "expansion"}}'
    parser = ResponseParser()
    
    with pytest.raises(ResponseParseException) as excinfo:
        parser.parse(incomplete_json)
    
    assert "Validation failed" in str(excinfo.value)

def test_parse_invalid_domain_values_raises_exception(valid_json_string):
    """허용되지 않은 errorCategory 또는 confidence.score 범위를 벗어날 경우 ResponseParseException 발생"""
    # 1. 잘못된 errorCategory.primary 주입
    data = json.loads(valid_json_string)
    data["errorCategory"]["primary"] = "INVALID_CATEGORY_CODE"
    json_str_invalid_cat = json.dumps(data)
    
    parser = ResponseParser()
    with pytest.raises(ResponseParseException) as excinfo:
        parser.parse(json_str_invalid_cat)
    assert "Validation failed" in str(excinfo.value)

    # 2. confidence.score 범위 이탈
    data2 = json.loads(valid_json_string)
    data2["confidence"]["score"] = 100.0  # ge 0.0, le 1.0 초과
    json_str_invalid_score = json.dumps(data2)
    
    with pytest.raises(ResponseParseException) as excinfo:
        parser.parse(json_str_invalid_score)
    assert "Validation failed" in str(excinfo.value)
