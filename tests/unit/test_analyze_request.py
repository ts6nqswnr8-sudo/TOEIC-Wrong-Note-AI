import pytest
from pydantic import ValidationError
from src.domain.models import AnalyzeRequest, TestType, ChoiceLabel

def test_valid_analyze_request():
    """정상적인 입력인 경우 ValidationError가 발생하지 않음"""
    req = AnalyzeRequest(
        test_type=TestType.RC,
        part=5,
        question_text="The ------- was successful.",
        choices={"A": "expand", "B": "expansion", "C": "expansive", "D": "expansively"},
        correct_answer=ChoiceLabel.B,
        user_answer=ChoiceLabel.C
    )
    assert req.question_text == "The ------- was successful."
    assert req.correct_answer == ChoiceLabel.B

def test_question_text_cannot_be_empty():
    """문제 내용이 비어 있으면(빈 문자열) 에러 발생"""
    with pytest.raises(ValidationError):
        AnalyzeRequest(
            test_type=TestType.RC,
            part=5,
            question_text="   ",
            choices={"A": "expand", "B": "expansion", "C": "expansive", "D": "expansively"},
            correct_answer=ChoiceLabel.B,
            user_answer=ChoiceLabel.C
        )

def test_user_answer_cannot_be_empty():
    """사용자가 선택한 답이 빈 문자열인 경우 에러 발생"""
    with pytest.raises(ValidationError):
        AnalyzeRequest(
            test_type=TestType.RC,
            part=5,
            question_text="The ------- was successful.",
            choices={"A": "expand", "B": "expansion", "C": "expansive", "D": "expansively"},
            correct_answer=ChoiceLabel.B,
            user_answer=""  # type: ignore
        )

def test_correct_answer_cannot_be_empty():
    """정답이 빈 문자열인 경우 에러 발생"""
    with pytest.raises(ValidationError):
        AnalyzeRequest(
            test_type=TestType.RC,
            part=5,
            question_text="The ------- was successful.",
            choices={"A": "expand", "B": "expansion", "C": "expansive", "D": "expansively"},
            correct_answer="",  # type: ignore
            user_answer=ChoiceLabel.C
        )

def test_user_answer_must_be_valid_choice():
    """사용자의 답은 반드시 제공된 선택지(choices)의 키 안에 존재해야 함"""
    with pytest.raises(ValidationError):
        AnalyzeRequest(
            test_type=TestType.RC,
            part=5,
            question_text="The ------- was successful.",
            choices={"A": "expand", "B": "expansion"},  # A, B만 제공됨
            correct_answer=ChoiceLabel.B,
            user_answer=ChoiceLabel.C # C는 제공되지 않음
        )

def test_correct_answer_must_be_valid_choice():
    """정답은 반드시 제공된 선택지(choices)의 키 안에 존재해야 함"""
    with pytest.raises(ValidationError):
        AnalyzeRequest(
            test_type=TestType.RC,
            part=5,
            question_text="The ------- was successful.",
            choices={"A": "expand", "B": "expansion"},  # A, B만 제공됨
            correct_answer=ChoiceLabel.D, # D는 제공되지 않음
            user_answer=ChoiceLabel.A
        )

def test_invalid_test_type():
    """LC, RC 외의 잘못된 값을 test_type에 입력할 수 없음"""
    with pytest.raises(ValidationError):
        AnalyzeRequest(
            test_type="SPEAKING", # 잘못된 유형
            part=5,
            question_text="The ------- was successful.",
            choices={"A": "expand", "B": "expansion", "C": "expansive", "D": "expansively"},
            correct_answer=ChoiceLabel.B,
            user_answer=ChoiceLabel.C
        )
