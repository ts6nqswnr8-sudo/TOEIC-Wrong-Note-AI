from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from src.domain.models import AnalyzeRequest, AnalysisResult
from src.domain.interfaces import NoteRepository
from src.application.services import AnalysisService, AnalysisException


def get_repository() -> NoteRepository:
    """Returns the operational SQLite Repository."""
    from src.infrastructure.sqlite_repository import SQLiteNoteRepository
    return SQLiteNoteRepository()


def get_analysis_service() -> AnalysisService:
    """Returns the operational AnalysisService orchestration."""
    from src.application.prompt_builder import PromptBuilder
    from src.application.response_parser import AnalysisResultParser
    from src.config.settings import settings
    from src.infrastructure.openai_client import OpenAIProvider
    from src.infrastructure.fake_llm_provider import FakeLLMProvider

    if settings.LLM_PROVIDER == "openai":
        provider = OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
    else:
        provider = FakeLLMProvider()

    return AnalysisService(
        prompt_builder=PromptBuilder(),
        llm_provider=provider,
        response_parser=AnalysisResultParser()
    )


router = APIRouter()


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_and_save_note(
    request: AnalyzeRequest,
    service: AnalysisService = Depends(get_analysis_service),
    repo: NoteRepository = Depends(get_repository)
):
    """
    POST /api/v1/analyze
    Analyzes user inputs, saves to SQLite repository, and returns structural AnalysisResult.
    """
    try:
        result = await service.analyze(request)
        saved = await repo.save(result)
        return saved
    except AnalysisException as e:
        # 안전 조치: 내부 오류 추적이나 구체 에러 메시지/API 키 노출을 격리 방어
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during wrong answer analysis."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error."
        )


@router.get("/notes", response_model=List[AnalysisResult])
async def get_all_notes(repo: NoteRepository = Depends(get_repository)):
    """
    GET /api/v1/notes
    Returns all archived wrong notes.
    """
    return await repo.find_all()


@router.get("/notes/{id}", response_model=AnalysisResult)
async def get_note_by_id(id: UUID, repo: NoteRepository = Depends(get_repository)):
    """
    GET /api/v1/notes/{id}
    Returns detailed AnalysisResult for a specific note ID.
    """
    note = await repo.find_by_id(id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong note not found."
        )
    return note


@router.delete("/notes/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_by_id(id: UUID, repo: NoteRepository = Depends(get_repository)):
    """
    DELETE /api/v1/notes/{id}
    Removes a note from the archive.
    """
    deleted = await repo.delete(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong note not found to delete."
        )
