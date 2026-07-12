import pytest
from pydantic import ValidationError

# 아래 항목들은 아직 src.domain.models에 구현되지 않았으므로 임포트 단계에서 에러가 납니다.
from src.domain.models import (
    AnalysisResult,
    Translation,
    CorrectAnswer,
    CorrectReason,
    WrongAnswerReason,
    ErrorCategory,
    LearningPoint,
    VocabularyItem,
    Confidence,
    ErrorCategoryCode,
    PartOfSpeech
)

@pytest.fixture
def valid_json_data():
    return {
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
            "secondary": None,
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

def test_valid_analysis_result_creation(valid_json_data):
    """정상적인 JSON 데이터로부터 AnalysisResult 모델이 성공적으로 생성되고, snake_case 속성 접근 및 alias 직렬화가 정상 동작함"""
    result = AnalysisResult.model_validate(valid_json_data)
    
    # 1. snake_case 방식의 속성 접근 확인
    assert result.translation.question == "그 회사의 새로운 시장으로의 -------은/는 성공적이었다."
    assert result.correct_answer.choice == "B"
    assert result.correct_answer.text == "expansion"
    assert result.correct_reason.grammar_rule == "소유격 + 명사"
    assert result.wrong_answer_reason.selected_choice == "C"
    assert result.error_category.primary == ErrorCategoryCode.PART_OF_SPEECH
    assert result.learning_point.title == "소유격 뒤 품사 판별법"
    assert len(result.vocabulary) == 1
    assert result.vocabulary[0].word == "expansion"
    assert result.confidence.score == 0.95
    
    # 2. by_alias=True 직렬화 시 camelCase로 변환되는지 확인
    dumped = result.model_dump(by_alias=True)
    assert "correctAnswer" in dumped
    assert "correctReason" in dumped
    assert "wrongAnswerReason" in dumped
    assert "errorCategory" in dumped
    assert "learningPoint" in dumped
    assert dumped["correctAnswer"]["choice"] == "B"

def test_missing_required_fields(valid_json_data):
    """필수 필드가 누락되었을 때 ValidationError 발생"""
    # translation 누락
    invalid_data = valid_json_data.copy()
    del invalid_data["translation"]
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(invalid_data)

def test_empty_or_whitespace_strings(valid_json_data):
    """필수 문자열 필드들에 빈 문자열이나 공백만 주는 경우 ValidationError 발생"""
    # question이 공백인 경우
    invalid_data = valid_json_data.copy()
    invalid_data["translation"] = {
        "question": "   ",
        "choices": {"A": "a", "B": "b", "C": "c", "D": "d"}
    }
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(invalid_data)

    # correctReason.summary가 빈 문자열인 경우
    invalid_data2 = valid_json_data.copy()
    invalid_data2["correctReason"] = {
        "summary": "",
        "detail": "상세설명",
        "grammarRule": None
    }
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(invalid_data2)

def test_confidence_score_range(valid_json_data):
    """confidence score가 0.0과 1.0 사이가 아닐 경우 ValidationError 발생"""
    # 1.0 초과
    invalid_data = valid_json_data.copy()
    invalid_data["confidence"] = {"score": 1.1, "reason": "높음"}
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(invalid_data)

    # 0.0 미만
    invalid_data2 = valid_json_data.copy()
    invalid_data2["confidence"] = {"score": -0.1, "reason": "낮음"}
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(invalid_data2)

def test_invalid_error_category(valid_json_data):
    """errorCategory가 허용된 유형의 Enum 값이 아닐 경우 ValidationError 발생"""
    invalid_data = valid_json_data.copy()
    invalid_data["errorCategory"] = {
        "primary": "INVALID_CATEGORY_CODE",
        "secondary": None,
        "description": "설명"
    }
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(invalid_data)

def test_vocabulary_item_requirements(valid_json_data):
    """vocabulary 배열 내 항목의 조건 검증"""
    # 필수 필드 누락
    invalid_data = valid_json_data.copy()
    invalid_data["vocabulary"] = [{
        "word": "word",
        "meaning": "뜻"
        # partOfSpeech, exampleSentence 누락
    }]
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(invalid_data)

    # 허용되지 않은 품사 Enum
    invalid_data2 = valid_json_data.copy()
    invalid_data2["vocabulary"] = [{
        "word": "word",
        "partOfSpeech": "unknown_part",
        "meaning": "뜻",
        "exampleSentence": "sentence"
    }]
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(invalid_data2)

def test_invalid_types(valid_json_data):
    """잘못된 타입 입력 시 ValidationError 발생"""
    # score가 float 형식이 아니라 딕셔너리 정보인 경우
    invalid_data = valid_json_data.copy()
    invalid_data["confidence"] = {"score": {"sub_score": 0.9}, "reason": "타입오류"}
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(invalid_data)
