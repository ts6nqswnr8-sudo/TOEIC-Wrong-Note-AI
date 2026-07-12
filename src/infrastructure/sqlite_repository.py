import sqlite3
import json
import asyncio
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.domain.interfaces import NoteRepository
from src.domain.models import AnalysisResult


class SQLiteNoteRepository(NoteRepository):
    """
    SQLite-backed implementation of NoteRepository.
    Uses Python's built-in sqlite3 module with asyncio.to_thread to provide non-blocking CRUD.
    """

    def __init__(self, db_path: str = "notes.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initializes database schema if tables do not exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                part INTEGER NOT NULL,
                translation TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                correct_reason TEXT NOT NULL,
                wrong_answer_reason TEXT NOT NULL,
                error_category TEXT NOT NULL,
                learning_point TEXT NOT NULL,
                vocabulary TEXT NOT NULL,
                confidence TEXT NOT NULL,
                disclaimer TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()

    def _save_sync(self, note: AnalysisResult) -> AnalysisResult:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # by_alias=True 직렬화를 통해 Pydantic camelCase 값들을 고스란히 획득
        dumped = note.model_dump(by_alias=True)

        cursor.execute(
            """
            INSERT OR REPLACE INTO notes (
                id, created_at, part, translation, correct_answer, 
                correct_reason, wrong_answer_reason, error_category, 
                learning_point, vocabulary, confidence, disclaimer
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(note.id),
                note.created_at.isoformat(),
                note.part,
                json.dumps(dumped.get("translation")),
                json.dumps(dumped.get("correctAnswer")),
                json.dumps(dumped.get("correctReason")),
                json.dumps(dumped.get("wrongAnswerReason")),
                json.dumps(dumped.get("errorCategory")),
                json.dumps(dumped.get("learningPoint")),
                json.dumps(dumped.get("vocabulary")),
                json.dumps(dumped.get("confidence")),
                dumped.get("disclaimer", "")
            )
        )
        conn.commit()
        conn.close()
        return note

    def _find_all_sync(self) -> List[AnalysisResult]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append(self._row_to_model(row))

        conn.close()
        return results

    def _find_by_id_sync(self, note_id: str) -> Optional[AnalysisResult]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()

        result = None
        if row:
            result = self._row_to_model(row)

        conn.close()
        return result

    def _delete_sync(self, note_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0

    def _row_to_model(self, row: sqlite3.Row) -> AnalysisResult:
        # DB JSON text 데이터를 다시 딕셔너리로 환산 후 model_validate 적용
        data = {
            "id": row["id"],
            "createdAt": row["created_at"],
            "part": row["part"],
            "translation": json.loads(row["translation"]),
            "correctAnswer": json.loads(row["correct_answer"]),
            "correctReason": json.loads(row["correct_reason"]),
            "wrongAnswerReason": json.loads(row["wrong_answer_reason"]),
            "errorCategory": json.loads(row["error_category"]),
            "learningPoint": json.loads(row["learning_point"]),
            "vocabulary": json.loads(row["vocabulary"]),
            "confidence": json.loads(row["confidence"]),
            "disclaimer": row["disclaimer"]
        }
        return AnalysisResult.model_validate(data)

    async def save(self, note: AnalysisResult) -> AnalysisResult:
        return await asyncio.to_thread(self._save_sync, note)

    async def find_all(self) -> List[AnalysisResult]:
        return await asyncio.to_thread(self._find_all_sync)

    async def find_by_id(self, note_id: UUID) -> Optional[AnalysisResult]:
        return await asyncio.to_thread(self._find_by_id_sync, str(note_id))

    async def delete(self, note_id: UUID) -> bool:
        return await asyncio.to_thread(self._delete_sync, str(note_id))
