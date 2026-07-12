import pytest
from fastapi import status
from fastapi.testclient import TestClient
from uuid import uuid4
from app import app
from src.domain.models import AnalyzeRequest, TestType, ChoiceLabel, AnalysisResult
from src.application.services import AnalysisService, AnalysisException
from src.presentation.api import get_repository, get_analysis_service
from tests.unit.test_llm_provider import FakeLLMProvider
from src.application.prompt_builder import PromptBuilder
from src.application.response_parser import AnalysisResultParser
from tests.unit.test_note_repository import InMemoryNoteRepository

@pytest.fixture
def fake_repo():
    return InMemoryNoteRepository()

@pytest.fixture
def fake_service():
    mock_response = """
    {
      "translation": {
        "question": "test question.",
        "choices": {"A": "a", "B": "b", "C": "c", "D": "d"}
      },
      "correctAnswer": {
        "choice": "B",
        "text": "b"
      },
      "correctReason": {
        "summary": "reason",
        "detail": "detail",
        "grammarRule": null
      },
      "wrongAnswerReason": {
        "selectedChoice": "C",
        "selectedText": "c",
        "summary": "wrong",
        "detail": "detail"
      },
      "errorCategory": {
        "primary": "VOCABULARY",
        "secondary": null,
        "description": "desc"
      },
      "learningPoint": {
        "title": "concept",
        "explanation": "expl",
        "examples": [
          {"english": "ex1", "korean": "ex1"},
          {"english": "ex2", "korean": "ex2"}
        ],
        "tip": "tip"
      },
      "vocabulary": [
        {
          "word": "word",
          "partOfSpeech": "adjective",
          "meaning": "mean",
          "exampleSentence": "sentence"
        }
      ],
      "confidence": {
        "score": 0.9,
        "reason": "clear"
      },
      "disclaimer": "disclaimer"
    }
    """
    return AnalysisService(
        prompt_builder=PromptBuilder(),
        llm_provider=FakeLLMProvider(mock_response),
        response_parser=AnalysisResultParser()
    )

@pytest.fixture
def client(fake_repo, fake_service):
    app.dependency_overrides[get_repository] = lambda: fake_repo
    app.dependency_overrides[get_analysis_service] = lambda: fake_service
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_api_analyze_and_save_success(client):
    """POST /api/v1/analyze가 요청 파싱, 분석 조율, 영속 연동을 문제없이 정상 실현하는지 검증"""
    payload = {
        "test_type": "RC",
        "part": 5,
        "question_text": "The project ------- was successful.",
        "choices": {"A": "a", "B": "b", "C": "c", "D": "d"},
        "correct_answer": "B",
        "user_answer": "C"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "id" in data
    assert "createdAt" in data
    assert data["part"] == 5
    assert data["errorCategory"]["primary"] == "VOCABULARY"

def test_api_analyze_service_exception_hides_internals(client, fake_service):
    """내부 예외나 OpenAI의 커넥션 API 키 유출을 방어하고 500 코드를 리턴하는지 검증"""
    class BadService(AnalysisService):
        async def analyze(self, request):
            raise AnalysisException("OpenAI Auth secret_api_key_xyz was revoked or expired!")

    app.dependency_overrides[get_analysis_service] = lambda: BadService(None, None, None)

    payload = {
        "test_type": "RC",
        "part": 5,
        "question_text": "The project ------- was successful.",
        "choices": {"A": "a", "B": "b", "C": "c", "D": "d"},
        "correct_answer": "B",
        "user_answer": "C"
    }
    response = client.post("/api/v1/analyze", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "secret_api_key_xyz" not in response.text
    assert "wrong answer analysis" in response.json()["detail"]

def test_api_get_notes_list(client, fake_repo):
    """GET /api/v1/notes 저장소 목록 조회가 정상 동작하는지 테스트"""
    response = client.get("/api/v1/notes")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0

def test_api_note_detail_and_delete_flow(client, fake_repo):
    """상세 조회(GET /notes/{id})와 삭제(DELETE /notes/{id}) 기능 플로우 검증"""
    raw_payload = {
        "test_type": TestType.RC,
        "part": 6,
        "question_text": "Detailed question example.",
        "choices": {"A": "a", "B": "b", "C": "c", "D": "d"},
        "correct_answer": ChoiceLabel.B,
        "user_answer": ChoiceLabel.C
    }
    analyze_req = AnalyzeRequest.model_validate(raw_payload)
    
    # 2. analyze 후 저장
    service = app.dependency_overrides[get_analysis_service]()
    import asyncio
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(service.analyze(analyze_req))
    loop.run_until_complete(fake_repo.save(result))
    
    note_id = str(result.id)

    # 3. GET 상세 조회 성공 테스트
    res_get = client.get(f"/api/v1/notes/{note_id}")
    assert res_get.status_code == status.HTTP_200_OK
    assert res_get.json()["id"] == note_id
    assert res_get.json()["part"] == 6

    # 4. DELETE 삭제 검증
    res_del = client.delete(f"/api/v1/notes/{note_id}")
    assert res_del.status_code == status.HTTP_204_NO_CONTENT

    # 5. 삭제 후 다시 조회는 404 리턴
    res_get_gone = client.get(f"/api/v1/notes/{note_id}")
    assert res_get_gone.status_code == status.HTTP_404_NOT_FOUND

def test_api_note_detail_not_found(client):
    """존재하지 않는 오답 상세 조회 요청 시 404 코드가 리턴되는지 검증"""
    wrong_id = str(uuid4())
    response = client.get(f"/api/v1/notes/{wrong_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]

def test_api_delete_note_not_found(client):
    """존재하지 않는 오답 삭제 요청 시 404 코드가 리턴되는지 검증"""
    wrong_id = str(uuid4())
    response = client.delete(f"/api/v1/notes/{wrong_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]
