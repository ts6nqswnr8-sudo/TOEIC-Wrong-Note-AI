# TOEIC Wrong Note AI — 기술 명세서 (Tech Spec)

> **버전**: 1.0.0  
> **최종 수정**: 2026-07-12  
> **관련 문서**: [ANALYSIS_GUIDE.md](./ANALYSIS_GUIDE.md)

---

## 목차

1. [기술 선택 이유](#1-기술-선택-이유)
2. [프론트엔드와 백엔드의 책임](#2-프론트엔드와-백엔드의-책임)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [API 명세](#4-api-명세)
5. [디렉터리 구조](#5-디렉터리-구조)
6. [데이터 모델](#6-데이터-모델)
7. [배포 구조](#7-배포-구조)
8. [보안](#8-보안)
9. [테스트 전략](#9-테스트-전략)
10. [향후 확장 방향](#10-향후-확장-방향)

---

## 1. 기술 선택 이유

### 1-1. 프론트엔드

| 기술 | 선택 이유 |
|------|----------|
| **React** | 컴포넌트 기반 아키텍처로 오답 카드·통계 차트 등 재사용 가능한 UI 단위를 효율적으로 관리. 광범위한 생태계와 커뮤니티 지원. |
| **TypeScript** | 정적 타입으로 AI 응답 JSON 파싱 시 타입 안전성 확보. `AnalysisResult` 등 도메인 인터페이스를 컴파일 타임에 검증. |
| **Vite** | HMR(Hot Module Replacement)이 빠르고 설정이 간결. React + TypeScript 프로젝트의 빌드 속도가 Webpack 대비 10배 이상 빠름. |
| **GitHub Pages** | 정적 빌드 파일 호스팅에 무료. GitHub Actions와 자연스럽게 연동되어 CI/CD 파이프라인 구성이 용이. |

### 1-2. 백엔드

| 기술 | 선택 이유 |
|------|----------|
| **Python** | OpenAI SDK 공식 지원 언어. 데이터 처리·프롬프트 엔지니어링에 강점. |
| **FastAPI** | 비동기 지원, 자동 OpenAPI 문서 생성, Pydantic 기반 요청/응답 유효성 검증. |
| **OpenAI API** | GPT 모델을 통한 오답 원인 분석·학습 조언 생성. 구조화된 JSON 응답(Structured Outputs) 지원. |
| **SQLite** | MVP 단계에서 파일 기반 DB로 서버 의존성 최소화. 단일 파일로 백업·이관 용이. |
| **PostgreSQL** | 프로덕션 확장 시 전환 대상. 동시 접속, JSON 컬럼, 전문 검색 등 고급 기능 활용. |

### 1-3. 공통

| 기술 | 선택 이유 |
|------|----------|
| **pytest** | 백엔드 Python 테스트의 사실상 표준. fixture, parametrize 등 강력한 기능. |
| **Vitest** | Vite 네이티브 테스트 러너. 프론트엔드 유닛 테스트와 빌드 도구 통합. |
| **GitHub Actions** | 코드 저장소 내 CI/CD 정의. PR 머지 시 자동 테스트·배포. |
| **환경변수 (`.env`)** | API 키를 코드에서 분리. `.env`는 `.gitignore`에 포함하여 유출 방지. |

---

## 2. 프론트엔드와 백엔드의 책임

### 2-1. 책임 분리 원칙

> **핵심**: GitHub Pages는 정적 사이트이므로 **OpenAI API 키를 프론트엔드에 절대 포함하지 않는다**.  
> 모든 AI 요청은 **반드시 백엔드 API를 경유**하여 처리한다.

```
┌─────────────────┐        HTTPS        ┌─────────────────┐        SDK        ┌──────────┐
│   프론트엔드     │  ───────────────▶   │    백엔드 API    │  ──────────────▶  │ OpenAI   │
│  (GitHub Pages)  │  ◀───────────────   │   (FastAPI)      │  ◀──────────────  │ API      │
│                 │    JSON Response    │                  │   JSON Response  │          │
└─────────────────┘                     └────────┬─────────┘                  └──────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │    Database      │
                                        │ (SQLite / PG)    │
                                        └─────────────────┘
```

### 2-2. 프론트엔드 책임

| 책임 영역 | 상세 |
|-----------|------|
| **UI 렌더링** | 오답 입력 폼, 분석 결과 카드, 통계 대시보드 표시 |
| **사용자 입력 수집** | 문제 텍스트, 선택지, 사용자 선택 오답, Part 번호 입력 |
| **API 호출** | 백엔드 `/api/v1/analyze` 엔드포인트로 분석 요청 전송 |
| **응답 표시** | AI 분석 결과를 `AnalysisResult` 타입으로 파싱하여 카드 형태로 렌더링 |
| **로컬 상태 관리** | 분석 이력 캐싱, 필터/정렬 상태 관리 |
| **에러 처리** | 네트워크 오류, API 에러 응답에 대한 사용자 안내 |

### 2-3. 백엔드 책임

| 책임 영역 | 상세 |
|-----------|------|
| **API 키 관리** | OpenAI API 키를 환경변수로 보관, 외부 노출 차단 |
| **프롬프트 구성** | `ANALYSIS_GUIDE.md`의 분류 기준을 시스템 프롬프트에 포함 |
| **LLM 호출** | OpenAI API에 구조화된 JSON 응답 요청 |
| **응답 검증** | Pydantic 모델로 AI 응답의 스키마 유효성 검증 |
| **데이터 저장** | 분석 결과를 DB에 영구 저장 |
| **통계 집계** | 오답 유형별·Part별·기간별 통계 쿼리 제공 |
| **CORS 관리** | GitHub Pages 도메인에 대한 CORS 허용 설정 |

---

## 3. 시스템 아키텍처

### 3-1. 전체 아키텍처 다이어그램

```
                     ┌──────────────────────────────────────────┐
                     │              사용자 브라우저               │
                     │                                          │
                     │  ┌──────────────────────────────────┐    │
                     │  │     React SPA (Vite Build)       │    │
                     │  │  ┌────────┐ ┌────────┐ ┌──────┐  │    │
                     │  │  │오답입력│ │분석결과│ │통계  │  │    │
                     │  │  │  폼   │ │  카드  │ │대시보드│ │    │
                     │  │  └────────┘ └────────┘ └──────┘  │    │
                     │  └──────────────┬───────────────────┘    │
                     └─────────────────┼────────────────────────┘
                                       │ HTTPS (fetch)
                                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                      백엔드 서버 (FastAPI)                        │
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────────┐   │
│  │   Router     │──▶│  Service     │──▶│  OpenAI Client       │   │
│  │ /api/v1/*   │   │  (비즈니스   │   │  (gpt-4o-mini)       │   │
│  │             │   │   로직)      │   │                      │   │
│  └─────────────┘   └──────┬──────┘   └──────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│                    ┌─────────────┐                                │
│                    │ Repository  │                                │
│                    │ (DB 접근)   │                                │
│                    └──────┬──────┘                                │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │  SQLite /   │
                     │ PostgreSQL  │
                     └─────────────┘
```

### 3-2. 요청 흐름 (Sequence)

```
사용자 → [프론트엔드] POST /api/v1/analyze
                        ↓
         [백엔드 Router] 요청 수신, Pydantic 검증
                        ↓
         [Service 계층] 프롬프트 조합 + OpenAI API 호출
                        ↓
         [OpenAI API] GPT 모델이 JSON 응답 생성
                        ↓
         [Service 계층] 응답 파싱 + 스키마 검증
                        ↓
         [Repository] DB에 분석 결과 저장
                        ↓
         [백엔드 Router] JSON 응답 반환
                        ↓
사용자 ← [프론트엔드] 분석 결과 카드 렌더링
```

### 3-3. 계층 구조 (Layered Architecture)

| 계층 | 역할 | 의존 방향 |
|------|------|----------|
| **Router (API)** | HTTP 요청/응답 처리, 입력 검증 | → Service |
| **Service** | 비즈니스 로직, 프롬프트 조합, AI 호출 | → Repository, OpenAI Client |
| **Repository** | 데이터 영구 저장·조회 (DB 추상화) | → Database |
| **Domain** | 타입 정의, 상수, 인터페이스 | ← 모든 계층에서 참조 |

---

## 4. API 명세

### 4-1. Base URL

| 환경 | URL |
|------|-----|
| 개발 (로컬) | `http://localhost:8000/api/v1` |
| 프로덕션 | `https://<backend-domain>/api/v1` |

### 4-2. 엔드포인트 목록

#### `POST /api/v1/analyze` — 오답 분석 요청

새 오답을 분석하고 결과를 반환한다.

**Request Body**

```json
{
  "part": 5,
  "questionText": "The company's ------- to the new market was successful.",
  "choices": {
    "A": "expand",
    "B": "expansion",
    "C": "expansive",
    "D": "expansively"
  },
  "correctAnswer": "B",
  "userAnswer": "C",
  "passageText": null,
  "userNote": "명사인 줄 알았는데 형용사를 골랐다"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `part` | `integer` (1-7) | ✅ | 토익 Part 번호 |
| `questionText` | `string` | ✅ | 문제 본문 텍스트 |
| `choices` | `object` | ✅ | 선택지 A~D (Part에 따라 A~C 가능) |
| `correctAnswer` | `string` | ✅ | 정답 기호 (A/B/C/D) |
| `userAnswer` | `string` | ✅ | 사용자가 고른 오답 기호 |
| `passageText` | `string \| null` | ❌ | 지문 텍스트 (Part 3,4,6,7) |
| `userNote` | `string \| null` | ❌ | 사용자 메모 |

**Response Body** — `200 OK`

`ANALYSIS_GUIDE.md` §3에 정의된 JSON 스키마를 따르는 `AnalysisResult` 객체를 반환한다. 응답은 `id`, `createdAt` 필드가 추가된다.

```json
{
  "id": "uuid-string",
  "createdAt": "2026-07-12T12:00:00Z",
  "part": 5,
  "translation": { "..." },
  "correctAnswer": { "..." },
  "correctReason": { "..." },
  "wrongAnswerReason": { "..." },
  "errorCategory": { "..." },
  "learningPoint": { "..." },
  "vocabulary": [ "..." ],
  "confidence": { "..." },
  "disclaimer": "..."
}
```

**Error Responses**

| 상태 코드 | 상황 | 응답 |
|-----------|------|------|
| `400` | 요청 데이터 유효성 검증 실패 | `{ "detail": "..." }` |
| `422` | Pydantic 검증 실패 | `{ "detail": [{ "loc": [...], "msg": "...", "type": "..." }] }` |
| `429` | OpenAI API Rate Limit 초과 | `{ "detail": "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요." }` |
| `500` | 서버 내부 오류 | `{ "detail": "분석 중 오류가 발생했습니다." }` |
| `503` | OpenAI API 서비스 불가 | `{ "detail": "AI 서비스에 일시적으로 연결할 수 없습니다." }` |

---

#### `GET /api/v1/notes` — 오답 노트 목록 조회

저장된 오답 노트 목록을 반환한다.

**Query Parameters**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `page` | `integer` | `1` | 페이지 번호 |
| `size` | `integer` | `20` | 페이지당 항목 수 (최대 100) |
| `part` | `integer \| null` | `null` | Part 번호 필터 |
| `errorCategory` | `string \| null` | `null` | 오답 유형 코드 필터 |
| `sortBy` | `string` | `createdAt` | 정렬 기준 (`createdAt`, `part`, `errorCategory`) |
| `order` | `string` | `desc` | 정렬 방향 (`asc`, `desc`) |

**Response Body** — `200 OK`

```json
{
  "items": [ { "id": "...", "part": 5, "errorCategory": "PART_OF_SPEECH", "createdAt": "...", "..." } ],
  "total": 42,
  "page": 1,
  "size": 20,
  "totalPages": 3
}
```

---

#### `GET /api/v1/notes/{id}` — 오답 노트 상세 조회

특정 오답 노트의 전체 분석 결과를 반환한다.

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `id` | `string (UUID)` | 오답 노트 ID |

**Response Body** — `200 OK`

전체 `AnalysisResult` 객체 (POST /analyze 응답과 동일 형태).

**Error** — `404 Not Found`

---

#### `DELETE /api/v1/notes/{id}` — 오답 노트 삭제

**Response** — `204 No Content`

---

#### `GET /api/v1/stats/summary` — 통계 요약

오답 유형별·Part별 통계를 반환한다.

**Query Parameters**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `period` | `string` | `all` | 기간 필터 (`7d`, `30d`, `90d`, `all`) |

**Response Body** — `200 OK`

```json
{
  "totalNotes": 120,
  "period": "30d",
  "byErrorCategory": [
    { "category": "PART_OF_SPEECH", "count": 25, "percentage": 20.8 },
    { "category": "VOCABULARY", "count": 18, "percentage": 15.0 }
  ],
  "byPart": [
    { "part": 5, "count": 45, "percentage": 37.5 },
    { "part": 7, "count": 30, "percentage": 25.0 }
  ],
  "recentTrend": [
    { "date": "2026-07-01", "count": 5 },
    { "date": "2026-07-02", "count": 3 }
  ]
}
```

---

#### `PATCH /api/v1/notes/{id}/override` — 사용자 오답 유형 오버라이드

AI 분석 결과를 사용자가 수정한다 (예: `CARELESS_MISTAKE`로 변경).

**Request Body**

```json
{
  "errorCategory": "CARELESS_MISTAKE",
  "reason": "이 문제는 알고 있었는데 마킹 실수였다"
}
```

**Response** — `200 OK`

업데이트된 `AnalysisResult` 객체.

---

#### `GET /api/v1/health` — 헬스 체크

**Response** — `200 OK`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "openai": "available"
}
```

---

## 5. 디렉터리 구조

### 5-1. 모노레포 전체 구조

```
TOEIC-Wrong-Note-AI/
├── docs/                          # 프로젝트 문서
│   ├── ANALYSIS_GUIDE.md          # 오답 분석 기준 가이드
│   └── TECH_SPEC.md               # 기술 명세서 (이 문서)
│
├── frontend/                      # 프론트엔드 (React + Vite)
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/                   # API 클라이언트
│   │   │   └── analysisApi.ts
│   │   ├── components/            # UI 컴포넌트
│   │   │   ├── AnalysisCard/
│   │   │   │   ├── AnalysisCard.tsx
│   │   │   │   └── AnalysisCard.module.css
│   │   │   ├── NoteForm/
│   │   │   │   ├── NoteForm.tsx
│   │   │   │   └── NoteForm.module.css
│   │   │   ├── StatsChart/
│   │   │   │   ├── StatsChart.tsx
│   │   │   │   └── StatsChart.module.css
│   │   │   └── common/
│   │   │       ├── Button.tsx
│   │   │       ├── Card.tsx
│   │   │       └── Loading.tsx
│   │   ├── hooks/                 # 커스텀 훅
│   │   │   ├── useAnalysis.ts
│   │   │   └── useNotes.ts
│   │   ├── pages/                 # 페이지 컴포넌트
│   │   │   ├── HomePage.tsx
│   │   │   ├── AnalyzePage.tsx
│   │   │   ├── NotesPage.tsx
│   │   │   └── StatsPage.tsx
│   │   ├── types/                 # TypeScript 타입 정의
│   │   │   ├── analysis.ts        # AnalysisResult 인터페이스
│   │   │   └── api.ts             # API 요청/응답 타입
│   │   ├── utils/                 # 유틸리티 함수
│   │   │   └── formatters.ts
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                       # 백엔드 (FastAPI)
│   ├── app/
│   │   ├── api/                   # API 라우터
│   │   │   ├── __init__.py
│   │   │   ├── router.py          # 라우터 등록
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── analyze.py     # POST /analyze
│   │   │       ├── notes.py       # CRUD /notes
│   │   │       └── stats.py       # GET /stats
│   │   ├── core/                  # 설정·보안
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # 환경변수 로드
│   │   │   └── security.py        # CORS, Rate Limit
│   │   ├── domain/                # 도메인 모델
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # Pydantic 모델 (스키마)
│   │   │   └── constants.py       # 오답 유형 코드 상수
│   │   ├── service/               # 비즈니스 로직
│   │   │   ├── __init__.py
│   │   │   ├── analysis_service.py
│   │   │   └── prompt_builder.py  # 프롬프트 조합기
│   │   ├── repository/            # DB 접근
│   │   │   ├── __init__.py
│   │   │   └── note_repository.py
│   │   ├── db/                    # 데이터베이스 설정
│   │   │   ├── __init__.py
│   │   │   ├── database.py        # 엔진·세션 관리
│   │   │   └── tables.py          # 테이블 정의 (SQLAlchemy)
│   │   └── main.py                # FastAPI 앱 엔트리포인트
│   ├── tests/                     # 테스트
│   │   ├── conftest.py            # pytest fixtures
│   │   ├── test_analyze.py
│   │   ├── test_notes.py
│   │   ├── test_stats.py
│   │   ├── test_prompt_builder.py
│   │   └── test_models.py
│   ├── .env.example               # 환경변수 템플릿
│   ├── requirements.txt
│   └── pyproject.toml
│
├── .github/
│   └── workflows/
│       ├── frontend-ci.yml        # 프론트엔드 CI/CD
│       └── backend-ci.yml         # 백엔드 CI
│
├── .gitignore
└── README.md
```

### 5-2. 디렉터리 설계 원칙

| 원칙 | 설명 |
|------|------|
| **모노레포** | `frontend/`와 `backend/`를 하나의 레포에서 관리하여 문서·이슈를 통합 추적 |
| **계층별 분리** | `api/`, `service/`, `repository/`, `domain/`으로 관심사를 분리 |
| **컴포넌트 코로케이션** | 프론트엔드 컴포넌트는 `.tsx`와 `.module.css`를 같은 폴더에 배치 |
| **타입 중앙 관리** | `types/` 폴더에 도메인 인터페이스를 모아 프론트엔드 전체에서 참조 |

---

## 6. 데이터 모델

### 6-1. ER 다이어그램

```
┌───────────────────────────────────────────┐
│                  notes                     │
├───────────────────────────────────────────┤
│ id              UUID         PK           │
│ created_at      TIMESTAMP    NOT NULL     │
│ updated_at      TIMESTAMP    NOT NULL     │
│ part            INTEGER      NOT NULL     │  ← 1~7
│ question_text   TEXT         NOT NULL     │
│ choices         JSON         NOT NULL     │  ← {"A": "...", "B": "..."}
│ correct_answer  VARCHAR(1)   NOT NULL     │  ← A/B/C/D
│ user_answer     VARCHAR(1)   NOT NULL     │
│ passage_text    TEXT         NULLABLE     │
│ user_note       TEXT         NULLABLE     │
│ translation     JSON         NOT NULL     │  ← AI 응답
│ correct_reason  JSON         NOT NULL     │  ← AI 응답
│ wrong_reason    JSON         NOT NULL     │  ← AI 응답
│ error_category  VARCHAR(30)  NOT NULL     │  ← primary 코드
│ error_secondary VARCHAR(30)  NULLABLE     │
│ error_detail    TEXT         NOT NULL     │
│ learning_point  JSON         NOT NULL     │  ← AI 응답
│ vocabulary      JSON         NOT NULL     │  ← AI 응답
│ confidence      REAL         NOT NULL     │  ← 0.0~1.0
│ is_overridden   BOOLEAN      DEFAULT FALSE│  ← 사용자 오버라이드 여부
│ override_reason TEXT         NULLABLE     │
└───────────────────────────────────────────┘
```

### 6-2. 인덱스

```sql
CREATE INDEX idx_notes_part           ON notes (part);
CREATE INDEX idx_notes_error_category ON notes (error_category);
CREATE INDEX idx_notes_created_at     ON notes (created_at DESC);
```

### 6-3. Pydantic 모델 (백엔드)

```python
# backend/app/domain/models.py

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ErrorCategoryCode(str, Enum):
    PART_OF_SPEECH = "PART_OF_SPEECH"
    VOCABULARY = "VOCABULARY"
    PREPOSITION_IDIOM = "PREPOSITION_IDIOM"
    SENTENCE_STRUCTURE = "SENTENCE_STRUCTURE"
    TENSE_VOICE = "TENSE_VOICE"
    AGREEMENT_PRONOUN = "AGREEMENT_PRONOUN"
    CONNECTOR = "CONNECTOR"
    EVIDENCE_FINDING = "EVIDENCE_FINDING"
    PARAPHRASING = "PARAPHRASING"
    LISTENING = "LISTENING"
    CARELESS_MISTAKE = "CARELESS_MISTAKE"
    OTHER = "OTHER"


class ChoiceLabel(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class AnalyzeRequest(BaseModel):
    part: int = Field(..., ge=1, le=7, description="토익 Part 번호")
    question_text: str = Field(..., alias="questionText", min_length=1)
    choices: dict[str, str] = Field(..., description="선택지 A~D")
    correct_answer: ChoiceLabel = Field(..., alias="correctAnswer")
    user_answer: ChoiceLabel = Field(..., alias="userAnswer")
    passage_text: Optional[str] = Field(None, alias="passageText")
    user_note: Optional[str] = Field(None, alias="userNote")


class Translation(BaseModel):
    question: str
    choices: dict[str, str]


class CorrectAnswer(BaseModel):
    choice: ChoiceLabel
    text: str


class CorrectReason(BaseModel):
    summary: str = Field(..., max_length=50)
    detail: str
    grammar_rule: Optional[str] = Field(None, alias="grammarRule")


class WrongAnswerReason(BaseModel):
    selected_choice: ChoiceLabel = Field(..., alias="selectedChoice")
    selected_text: str = Field(..., alias="selectedText")
    summary: str = Field(..., max_length=50)
    detail: str


class ErrorCategory(BaseModel):
    primary: ErrorCategoryCode
    secondary: Optional[ErrorCategoryCode] = None
    description: str


class ExampleSentence(BaseModel):
    english: str
    korean: str


class LearningPoint(BaseModel):
    title: str
    explanation: str
    examples: list[ExampleSentence] = Field(..., min_length=2, max_length=3)
    tip: str


class PartOfSpeech(str, Enum):
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    PHRASE = "phrase"


class VocabularyItem(BaseModel):
    word: str
    part_of_speech: PartOfSpeech = Field(..., alias="partOfSpeech")
    meaning: str
    example_sentence: str = Field(..., alias="exampleSentence")


class Confidence(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    reason: str


class AnalysisResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    part: int
    translation: Translation
    correct_answer: CorrectAnswer = Field(..., alias="correctAnswer")
    correct_reason: CorrectReason = Field(..., alias="correctReason")
    wrong_answer_reason: WrongAnswerReason = Field(..., alias="wrongAnswerReason")
    error_category: ErrorCategory = Field(..., alias="errorCategory")
    learning_point: LearningPoint = Field(..., alias="learningPoint")
    vocabulary: list[VocabularyItem] = Field(..., min_length=1, max_length=5)
    confidence: Confidence
    disclaimer: str
```

### 6-4. TypeScript 인터페이스 (프론트엔드)

```typescript
// frontend/src/types/analysis.ts

export type ChoiceLabel = 'A' | 'B' | 'C' | 'D';

export type ErrorCategoryCode =
  | 'PART_OF_SPEECH'
  | 'VOCABULARY'
  | 'PREPOSITION_IDIOM'
  | 'SENTENCE_STRUCTURE'
  | 'TENSE_VOICE'
  | 'AGREEMENT_PRONOUN'
  | 'CONNECTOR'
  | 'EVIDENCE_FINDING'
  | 'PARAPHRASING'
  | 'LISTENING'
  | 'CARELESS_MISTAKE'
  | 'OTHER';

export interface AnalyzeRequest {
  part: number;
  questionText: string;
  choices: Record<ChoiceLabel, string>;
  correctAnswer: ChoiceLabel;
  userAnswer: ChoiceLabel;
  passageText?: string | null;
  userNote?: string | null;
}

export interface AnalysisResult {
  id: string;
  createdAt: string;
  part: number;
  translation: {
    question: string;
    choices: Record<ChoiceLabel, string>;
  };
  correctAnswer: {
    choice: ChoiceLabel;
    text: string;
  };
  correctReason: {
    summary: string;
    detail: string;
    grammarRule: string | null;
  };
  wrongAnswerReason: {
    selectedChoice: ChoiceLabel;
    selectedText: string;
    summary: string;
    detail: string;
  };
  errorCategory: {
    primary: ErrorCategoryCode;
    secondary: ErrorCategoryCode | null;
    description: string;
  };
  learningPoint: {
    title: string;
    explanation: string;
    examples: { english: string; korean: string }[];
    tip: string;
  };
  vocabulary: {
    word: string;
    partOfSpeech: string;
    meaning: string;
    exampleSentence: string;
  }[];
  confidence: {
    score: number;
    reason: string;
  };
  disclaimer: string;
}
```

---

## 7. 배포 구조

### 7-1. 배포 개요

| 대상 | 호스팅 | 배포 트리거 | URL |
|------|--------|------------|-----|
| **프론트엔드** | GitHub Pages | `main` 브랜치 push → GitHub Actions | `https://<user>.github.io/TOEIC-Wrong-Note-AI/` |
| **백엔드** | 서버리스 (선택) | `main` 브랜치 push → GitHub Actions | `https://<backend-domain>/api/v1` |

### 7-2. 백엔드 서버리스 배포 옵션

| 플랫폼 | 무료 티어 | 특징 | 권장 |
|--------|----------|------|------|
| **Render** | 750시간/월 | Dockerfile 또는 Python 런타임 직접 배포 | ✅ MVP 추천 |
| **Railway** | $5 크레딧/월 | GitHub 연동 자동 배포, 무료 PostgreSQL | 확장 시 |
| **Fly.io** | 3 공유 VM | Docker 기반, 글로벌 엣지 배포 | 고가용성 |
| **Vercel (Serverless Functions)** | 무료 | Python Serverless Function 지원 | 간단한 API |

### 7-3. GitHub Actions 워크플로우

#### 프론트엔드 CI/CD (`frontend-ci.yml`)

```yaml
name: Frontend CI/CD

on:
  push:
    branches: [main]
    paths: ['frontend/**', 'docs/**']
  pull_request:
    branches: [main]
    paths: ['frontend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm run test -- --run
      - run: npm run build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    permissions:
      pages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run build
        env:
          VITE_API_BASE_URL: ${{ vars.API_BASE_URL }}
      - uses: actions/upload-pages-artifact@v3
        with:
          path: frontend/dist
      - uses: actions/deploy-pages@v4
```

#### 백엔드 CI (`backend-ci.yml`)

```yaml
name: Backend CI

on:
  push:
    branches: [main]
    paths: ['backend/**']
  pull_request:
    branches: [main]
    paths: ['backend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov pytest-asyncio
      - run: pytest --cov=app --cov-report=term-missing
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          DATABASE_URL: "sqlite:///./test.db"
```

---

## 8. 보안

### 8-1. API 키 보호

| 규칙 | 상세 |
|------|------|
| **프론트엔드에 API 키 금지** | OpenAI API 키는 백엔드 환경변수에만 존재. GitHub Pages 빌드에 절대 포함하지 않음. |
| **`.env` 파일 관리** | `.env`는 `.gitignore`에 등록. `.env.example`에 키 없는 템플릿만 커밋. |
| **GitHub Secrets** | CI/CD에서 사용하는 키는 GitHub Repository Secrets에 저장. |

```
# backend/.env.example
APP_ENV=development
LLM_PROVIDER=fake
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./toeic.db
```

### 8-3. 환경 변수 및 LLM Provider 선택 정책

로컬 데브서버와 테스트 실행 시 불필요한 API 과금을 막고 안정성을 확보하기 위해 환경별 LLM Provider를 다르게 동작시킵니다.

| 환경 변수 | 허용/기본값 | 설명 |
|---|---|---|
| `APP_ENV` | `development`, `testing`, `production` (기본값: `development`) | 애플리케이션 실행 환경 모드 |
| `LLM_PROVIDER` | `fake`, `openai` (기본값: `fake`) | LLM 모델 호출 모드 선택 |
| `OPENAI_API_KEY` | 문자열 (기본값: 빈 문자열) | OpenAI API 인증 키 |
| `OPENAI_MODEL` | `gpt-4o-mini` 등 (기본값: `gpt-4o-mini`) | OpenAI 모델 식별자 |
| `DATABASE_URL` | `sqlite:///./toeic.db` | 데이터베이스 연결 주소 |

#### 연동 및 유효성 검증 규칙 (Pydantic Settings):
1. **운영 환경 강제 정책**: `APP_ENV=production`인 경우, `LLM_PROVIDER`는 반드시 `openai`여야 합니다. (`fake` 사용 불가)
2. **API 키 존재 여부 검증**: `LLM_PROVIDER=openai` 설정 시 `OPENAI_API_KEY`가 생략되거나 비어 있으면 애플리케이션 시작 단계에서 즉시 오류(`ValueError`)를 발생시킵니다.
3. **가짜(Fake) 모드 식별**: `FakeLLMProvider`는 API 요청 인자(질문, 선택지 등)를 수신해서 `ANALYSIS_GUIDE.md` 스펙의 dynamic mock JSON 응답을 돌려줍니다. 이때 디스클레이머(`disclaimer`) 값을 통해 "FakeLLMProvider(가짜 모델)"가 사용되었음을 알립니다.


### 8-2. CORS 설정

```python
# backend/app/core/security.py

from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    allowed_origins = [
        settings.allowed_origins,       # 프로덕션: GitHub Pages URL
        "http://localhost:5173",         # 개발: Vite dev server
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type"],
    )
```

### 8-3. Rate Limiting

| 대상 | 제한 | 이유 |
|------|------|------|
| `POST /analyze` | **10 req/분/IP** | OpenAI API 비용 보호 |
| `GET /notes` | **60 req/분/IP** | 일반적 REST 제한 |
| `GET /stats` | **30 req/분/IP** | 집계 쿼리 부하 제한 |

```python
# slowapi 또는 커스텀 미들웨어 사용
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/analyze")
@limiter.limit("10/minute")
async def analyze(request: Request, body: AnalyzeRequest):
    ...
```

### 8-4. 입력 검증

| 규칙 | 구현 |
|------|------|
| 요청 크기 제한 | `questionText` 최대 2,000자, `passageText` 최대 5,000자 |
| 선택지 검증 | `choices`는 최소 2개, 최대 4개의 키 필수 |
| Part 범위 검증 | `part`는 1~7 정수만 허용 |
| SQL Injection 방지 | SQLAlchemy ORM 사용으로 파라미터 바인딩 자동 적용 |

---

## 9. 테스트 전략

### 9-1. 테스트 계층

```
                    ┌─────────────────────┐
                    │   수동 테스트 (UI)    │  ← 시각적 확인, 사용성
                    ├─────────────────────┤
                    │   통합 테스트        │  ← API 엔드포인트 E2E
                    ├─────────────────────┤
                    │   단위 테스트        │  ← 비즈니스 로직, 모델
                    └─────────────────────┘
                    (피라미드 — 아래가 가장 많음)
```

### 9-2. 백엔드 테스트 (pytest)

| 테스트 대상 | 파일 | 테스트 내용 |
|------------|------|------------|
| **Pydantic 모델** | `test_models.py` | 유효/무효 입력 검증, enum 값 확인, 필수 필드 누락 시 에러 |
| **프롬프트 빌더** | `test_prompt_builder.py` | Part별 프롬프트 차이, 선택지 포맷, 시스템 프롬프트 포함 여부 |
| **분석 서비스** | `test_analyze.py` | OpenAI 응답 모킹, 응답 파싱 검증, 에러 시 fallback |
| **API 라우터** | `test_notes.py` | CRUD 엔드포인트 HTTP 상태 코드, 페이지네이션, 필터 |
| **통계** | `test_stats.py` | 유형별·Part별 집계 정확성, 기간 필터 |

```python
# 예시: test_models.py
import pytest
from app.domain.models import AnalyzeRequest, ErrorCategoryCode

class TestAnalyzeRequest:
    def test_valid_request(self):
        req = AnalyzeRequest(
            part=5,
            questionText="The ------- was successful.",
            choices={"A": "expand", "B": "expansion", "C": "expansive", "D": "expansively"},
            correctAnswer="B",
            userAnswer="C"
        )
        assert req.part == 5
        assert req.correct_answer == "B"

    def test_invalid_part_raises(self):
        with pytest.raises(ValueError):
            AnalyzeRequest(
                part=8,  # 범위 초과
                questionText="test",
                choices={"A": "a", "B": "b", "C": "c", "D": "d"},
                correctAnswer="A",
                userAnswer="B"
            )

    @pytest.mark.parametrize("code", ErrorCategoryCode)
    def test_all_error_categories_valid(self, code):
        assert code.value in [
            "PART_OF_SPEECH", "VOCABULARY", "PREPOSITION_IDIOM",
            "SENTENCE_STRUCTURE", "TENSE_VOICE", "AGREEMENT_PRONOUN",
            "CONNECTOR", "EVIDENCE_FINDING", "PARAPHRASING",
            "LISTENING", "CARELESS_MISTAKE", "OTHER"
        ]
```

### 9-3. 프론트엔드 테스트 (Vitest)

| 테스트 대상 | 테스트 내용 |
|------------|------------|
| **타입 가드** | API 응답이 `AnalysisResult` 인터페이스에 부합하는지 런타임 검증 |
| **유틸리티 함수** | 날짜 포맷, 퍼센트 계산, 에러 카테고리 라벨 변환 |
| **커스텀 훅** | `useAnalysis`, `useNotes`의 상태 전이 (loading → success/error) |

### 9-4. OpenAI API 모킹 전략

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_openai_response():
    """OpenAI API를 모킹하여 비용 없이 테스트"""
    mock_response = {
        "translation": {"question": "테스트 문제", "choices": {"A": "a", "B": "b", "C": "c", "D": "d"}},
        "correctAnswer": {"choice": "B", "text": "expansion"},
        "correctReason": {"summary": "명사 자리", "detail": "...", "grammarRule": "소유격 + 명사"},
        "wrongAnswerReason": {"selectedChoice": "C", "selectedText": "expansive", "summary": "형용사 오선택", "detail": "..."},
        "errorCategory": {"primary": "PART_OF_SPEECH", "secondary": None, "description": "..."},
        "learningPoint": {"title": "품사 판별", "explanation": "...", "examples": [{"english": "...", "korean": "..."},{"english": "...", "korean": "..."}], "tip": "..."},
        "vocabulary": [{"word": "expansion", "partOfSpeech": "noun", "meaning": "확장", "exampleSentence": "..."}],
        "confidence": {"score": 0.95, "reason": "..."},
        "disclaimer": "..."
    }

    with patch("app.service.analysis_service.openai_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        yield mock_client
```

### 9-5. CI 테스트 실행

| 단계 | 명령어 | 실패 시 |
|------|--------|---------|
| 백엔드 린트 | `ruff check .` | PR 머지 차단 |
| 백엔드 테스트 | `pytest --cov=app --cov-fail-under=80` | PR 머지 차단 |
| 프론트엔드 린트 | `npm run lint` | PR 머지 차단 |
| 프론트엔드 테스트 | `npx vitest --run` | PR 머지 차단 |
| 프론트엔드 빌드 | `npm run build` | 배포 중단 |

---

## 10. 향후 확장 방향

### 10-1. 단기 (v1.x)

| 기능 | 설명 |
|------|------|
| **사용자 인증** | GitHub OAuth 또는 이메일 로그인으로 개인 오답 노트 관리 |
| **오답 노트 내보내기** | PDF/CSV 형태로 오답 노트 다운로드 |
| **학습 알림** | 에빙하우스 망각 곡선 기반 복습 알림 (이메일 또는 브라우저 알림) |
| **이미지 OCR 입력** | 문제집 사진 촬영 → OCR로 텍스트 자동 추출 (OpenAI Vision API) |

### 10-2. 중기 (v2.x)

| 기능 | 설명 |
|------|------|
| **SQLite → PostgreSQL 전환** | 다중 사용자 지원을 위한 DB 스케일업 |
| **실시간 통계 대시보드** | 주간·월간 트렌드, 취약 유형 히트맵, 점수 예측 |
| **AI 모델 업그레이드** | GPT-4o 또는 최신 모델로 분석 정확도 향상 |
| **오답 유형 자동 세분화** | `OTHER`로 누적된 데이터를 클러스터링하여 새 유형 제안 |

### 10-3. 장기 (v3.x+)

| 기능 | 설명 |
|------|------|
| **모바일 앱** | React Native 또는 PWA로 모바일 기기 지원 |
| **커뮤니티 기능** | 오답 노트 공유, 학습 그룹, 랭킹 시스템 |
| **맞춤형 문제 추천** | 취약 유형 기반 AI 문제 생성 및 추천 |
| **다국어 확장** | TOEFL, IELTS, JLPT 등 다른 시험 지원 |

---

> **이 문서는 프로젝트의 기술적 의사결정과 구현 방향의 기준 문서입니다.**  
> 기술 스택이나 아키텍처를 변경할 때는 반드시 이 문서를 먼저 업데이트하세요.
