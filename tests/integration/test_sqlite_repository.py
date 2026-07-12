import os
import pytest
from uuid import uuid4
from src.domain.models import AnalysisResult
from src.infrastructure.sqlite_repository import SQLiteNoteRepository

@pytest.fixture
def temp_db_path(tmp_path):
    """임시 데이터베이스 경로 제공 장치"""
    db_file = tmp_path / "test_notes.db"
    return str(db_file)

@pytest.fixture
def dummy_record():
    data = {
        "id": str(uuid4()),
        "createdAt": "2026-07-12T14:32:00Z",
        "part": 5,
        "translation": {
            "question": "test question ------- syntax check.",
            "choices": {"A": "a", "B": "b", "C": "c", "D": "d"}
        },
        "correctAnswer": {
            "choice": "B",
            "text": "b"
        },
        "correctReason": {
            "summary": "합당",
            "detail": "설명",
            "grammarRule": None
        },
        "wrongAnswerReason": {
            "selectedChoice": "C",
            "selectedText": "c",
            "summary": "부적합",
            "detail": "설명"
        },
        "errorCategory": {
            "primary": "VOCABULARY",
            "secondary": None,
            "description": "어휘오류"
        },
        "learningPoint": {
            "title": "학습포인트",
            "explanation": "설명",
            "examples": [
                {"english": "ex1", "korean": "ex1"},
                {"english": "ex2", "korean": "ex2"}
            ],
            "tip": "팁"
        },
        "vocabulary": [
            {
                "word": "word",
                "partOfSpeech": "adverb",
                "meaning": "뜻",
                "exampleSentence": "ex"
            }
        ],
        "confidence": {
            "score": 0.88,
            "reason": "적당"
        },
        "disclaimer": "면책문"
    }
    return AnalysisResult.model_validate(data)

@pytest.mark.asyncio
async def test_sqlite_repository_crud(temp_db_path, dummy_record):
    """SQLite 저장소 구현체가 CRUD 요건을 온전히 지원하는지 확인"""
    # 0. 생성 및 테이블 준비
    repo = SQLiteNoteRepository(db_path=temp_db_path)

    # 1. find_all 0개 확인 (초기)
    all_notes = await repo.find_all()
    assert len(all_notes) == 0

    # 2. save (저장)
    saved = await repo.save(dummy_record)
    assert saved.id == dummy_record.id

    # 3. find_by_id (상세 조회 및 역직렬화 완성도 검증)
    found = await repo.find_by_id(dummy_record.id)
    assert found is not None
    assert found.id == dummy_record.id
    assert found.part == 5
    assert found.error_category.primary.value == "VOCABULARY"
    assert found.learning_point.title == "학습포인트"
    assert len(found.vocabulary) == 1

    # 4. find_all (전체 정렬 조회)
    all_notes = await repo.find_all()
    assert len(all_notes) == 1
    assert all_notes[0].id == dummy_record.id

    # 5. delete (삭제)
    deleted = await repo.delete(dummy_record.id)
    assert deleted is True

    # 6. 삭제 후 데이터 소거 확인
    found_after_del = await repo.find_by_id(dummy_record.id)
    assert found_after_del is None

    # 7. 기삭제된 잉여 식별자 삭제 재시도 시 False 반환
    deleted_again = await repo.delete(dummy_record.id)
    assert deleted_again is False
