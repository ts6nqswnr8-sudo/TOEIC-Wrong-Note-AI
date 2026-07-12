import pytest
from uuid import uuid4, UUID
from src.domain.interfaces import NoteRepository
from src.domain.models import AnalysisResult

# 1단계 TDD Red Phase: NoteRepository 인터페이스가 src/domain/interfaces에 구성되어 있지 않아 가져오기 실패함

class InMemoryNoteRepository(NoteRepository):
    """테스트용 인메모리 오답 노트 저장소 구현체"""
    def __init__(self) -> None:
        self._store = {}

    async def save(self, note: AnalysisResult) -> AnalysisResult:
        self._store[note.id] = note
        return note

    async def find_all(self) -> list[AnalysisResult]:
        return list(self._store.values())

    async def find_by_id(self, note_id: UUID) -> AnalysisResult | None:
        return self._store.get(note_id)

    async def delete(self, note_id: UUID) -> bool:
        if note_id in self._store:
            del self._store[note_id]
            return True
        return False

@pytest.fixture
def dummy_analysis_result():
    # AnalysisResult 유효 규격의 더미 객체 생성
    data = {
        "id": str(uuid4()),
        "createdAt": "2026-07-12T14:30:00Z",
        "part": 5,
        "translation": {
            "question": "The company's ------- to the new market was successful.",
            "choices": {"A": "expand", "B": "expansion", "C": "expansive", "D": "expansively"}
        },
        "correctAnswer": {
            "choice": "B",
            "text": "expansion"
        },
        "correctReason": {
            "summary": "명사 필요",
            "detail": "소유격 수식",
            "grammarRule": "소유격 + 명사"
        },
        "wrongAnswerReason": {
            "selectedChoice": "C",
            "selectedText": "expansive",
            "summary": "주어 불가",
            "detail": "형용사는 부적합"
        },
        "errorCategory": {
            "primary": "PART_OF_SPEECH",
            "secondary": None,
            "description": "품사 오류"
        },
        "learningPoint": {
            "title": "소유격 뒤 명사",
            "explanation": "개념설명",
            "examples": [
                {"english": "ex1", "korean": "ex1"},
                {"english": "ex2", "korean": "ex2"}
            ],
            "tip": "꿀팁"
        },
        "vocabulary": [
            {
                "word": "expansion",
                "partOfSpeech": "noun",
                "meaning": "확장",
                "exampleSentence": "The expansion was great."
            }
        ],
        "confidence": {
            "score": 0.95,
            "reason": "명확함"
        },
        "disclaimer": "AI 면책 조항"
    }
    return AnalysisResult.model_validate(data)

@pytest.mark.asyncio
async def test_repository_save_and_find_by_id(dummy_analysis_result):
    """오답 노트를 저장한 후 식별자 ID를 가지고 다시 조회할 수 있는지 검증"""
    repo = InMemoryNoteRepository()
    
    saved = await repo.save(dummy_analysis_result)
    assert saved.id == dummy_analysis_result.id
    
    retrieved = await repo.find_by_id(dummy_analysis_result.id)
    assert retrieved is not None
    assert retrieved.translation.question == dummy_analysis_result.translation.question

@pytest.mark.asyncio
async def test_repository_find_all(dummy_analysis_result):
    """저장된 모든 오답 노트를 한꺼번에 리스트 배열로 호출할 수 있는지 검증"""
    repo = InMemoryNoteRepository()
    
    # 0개 확인
    notes = await repo.find_all()
    assert len(notes) == 0
    
    # 1개 저장 후 1개 확인
    await repo.save(dummy_analysis_result)
    notes = await repo.find_all()
    assert len(notes) == 1
    assert notes[0].id == dummy_analysis_result.id

@pytest.mark.asyncio
async def test_repository_delete(dummy_analysis_result):
    """저장된 오답 노트를 삭제 처리하고 나면 더 이상 아이디로 검색할 수 없는지 검증"""
    repo = InMemoryNoteRepository()
    
    await repo.save(dummy_analysis_result)
    
    # 확실히 있는지 검증
    exists = await repo.find_by_id(dummy_analysis_result.id)
    assert exists is not None
    
    # 삭제 실행
    deleted = await repo.delete(dummy_analysis_result.id)
    assert deleted is True
    
    # 이제 조회하면 None 처리
    not_exists = await repo.find_by_id(dummy_analysis_result.id)
    assert not_exists is None

@pytest.mark.asyncio
async def test_repository_delete_non_existent():
    """존재하지 않는 잉여 식별자 삭제 요청 시 False 반환 검증"""
    repo = InMemoryNoteRepository()
    deleted = await repo.delete(uuid4())
    assert deleted is False
