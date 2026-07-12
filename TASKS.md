# TOEIC Wrong Note AI - Tasks & Tracker

이 문서는 `docs/TECH_SPEC.md` 및 `docs/ANALYSIS_GUIDE.md`를 바탕으로 작성된 전체 프로젝트의 작업(Task) 백로그입니다.
각 작업은 단일 PR 또는 명확한 커밋 단위로 설계되었으며, 상태(Status)를 업데이트하며 추적합니다.

---

## 📈 프로젝트 진행 상황
- [ ] Phase 0. 프로젝트 설정 (0/2)
- [ ] Phase 1. 도메인 모델과 입력 검증 (2/3)
- [ ] Phase 2. AI 분석 요청과 응답 파싱 (2/3)
- [ ] Phase 3. 오답 저장 및 조회 (0/4)
- [ ] Phase 4. UI 개발 (React / Streamlit 고려) (0/4)
- [ ] Phase 5. 통계 및 대시보드 (0/2)
- [ ] Phase 6. 배포 (0/3)
- [ ] Phase 7. 문서화와 포트폴리오 정리 (0/2)

---

## Phase 0. 프로젝트 설정

### [TASK-001] 백엔드 및 의존성 초기 설정
* **목적**: Python 가상 환경 설정 및 백엔드 개발에 필요한 기본 패키지 구성
* **세부 작업**: 
  - `requirements.txt` 정의 (`fastapi`, `pydantic`, `openai`, `pytest` 등)
  - `pyproject.toml` 파일에 pytest 설정 구성
  - `.env.example` 및 `.gitignore` 구성 완료
* **선행 작업**: 없음
* **완료 조건**: `pip install -r requirements.txt`가 성공하고, `pytest` 실행 시 오류 없이 빈 결과가 나와야 함
* **테스트 필요**: 아니오
* **결과 파일**: `requirements.txt`, `pyproject.toml`, `.env.example`, `.gitignore`

### [TASK-002] GitHub Actions CI/CD 파이프라인 구성
* **목적**: PR 및 병합 시 자동으로 코드 품질을 검증하는 환경 구축
* **세부 작업**:
  - Push 및 PR 시 동작하는 `backend-ci.yml` 작성
  - 백엔드 린터(`flake8` 또는 `ruff`) 및 테스트 스크립트 실행 추가
* **선행 작업**: [TASK-001]
* **완료 조건**: 임의의 PR을 생성했을 때 GitHub Actions에서 테스트 파이프라인이 정상 동작하고 Passed 상태를 반환함
* **테스트 필요**: 아니오
* **결과 파일**: `.github/workflows/backend-ci.yml`

---

## Phase 1. 도메인 모델과 입력 검증

### [TASK-101] AI 분석 응답 도메인 모델 구현 (완료)
* **목적**: `ANALYSIS_GUIDE.md`에 파편화된 JSON 스키마를 Pydantic 모델로 정의
* **세부 작업**:
  - 오답 유형(ErrorCategoryCode)과 PartOfSpeech 등 Enum 구현
  - `Translation`, `CorrectReason`, `WrongAnswerReason`, `LearningPoint`, `VocabularyItem`, `Confidence`, `AnalysisResult` Pydantic 모델 구현
* **선행 작업**: [TASK-001]
* **완료 조건**: Pydantic 모델 정의가 완료되고, 타입 힌팅 오류(Type Check)가 없어야 함
* **테스트 필요**: 예 (TDD 대상 - 유효한 JSON 주입 시 객체 생성 테스트)
* **결과 파일**: `src/domain/models.py`, `tests/unit/test_domain_models.py`

### [TASK-102] 오답 노트 입력 모델 설계 (AnalyzeRequest) (완료)
* **목적**: 사용자가 API로 전송할 오답 분석 요청 스키마 유효성 검증
* **세부 작업**:
  - `AnalyzeRequest` 모델 구현
  - Part 번호 1~7 제한(`ge=1`, `le=7`), 문제 텍스트 필수(`min_length=1`) 등의 검증 로직 추가
* **선행 작업**: [TASK-101]
* **완료 조건**: `part=8`과 같은 비정상 데이터 입력 시 Pydantic ValidationError를 발생시킴
* **테스트 필요**: 예 (TDD 대상 - 입력 검증 테스트)
* **결과 파일**: `src/domain/models.py`, `tests/unit/test_analyze_request.py`

### [TASK-103] 외부 인터페이스(Interface) 추상화
* **목적**: SOLID(DIP) 원칙 준수를 위한 Repository 및 AI 서비스의 인터페이스 정의
* **세부 작업**:
  - `NoteRepository` 프로토콜(또는 ABC) 작성
  - `AIService` 프로토콜(또는 ABC) 작성
* **선행 작업**: 없음
* **완료 조건**: 구체적인 구현 없이 추상화된 메서드 시그니처가 정의됨
* **테스트 필요**: 아니오
* **결과 파일**: `src/domain/interfaces.py`

---

## Phase 2. AI 분석 요청과 응답 파싱

### [TASK-201] AI 프롬프트 빌더 구현 (완료)
* **목적**: `AnalyzeRequest`를 입력받아 AI에게 전송할 최적화된 프롬프트 문자열 조합
* **세부 작업**:
  - `ANALYSIS_GUIDE.md` 내용을 주입하는 시스템 프롬프트 관리자 구축
  - 사용자의 입력값을 유저 프롬프트 포맷으로 렌더링하는 함수 생성
* **선행 작업**: [TASK-102]
* **완료 조건**: 요청 데이터를 넣었을 때 정확한 텍스트 템플릿(문자열 매핑)이 반환됨 
* **테스트 필요**: 예 (TDD 대상)
* **결과 파일**: `src/application/prompt_builder.py`, `tests/unit/test_prompt_builder.py`

### [TASK-202] OpenAI 연동 클라이언트 (인프라스트럭처)
* **목적**: 실제 OpenAI API를 호출하고 Structured Output(JSON)을 파싱하는 구현체 작성
* **세부 작업**:
  - `openai-python` 라이브러리를 활용한 `OpenAIClient` 클래스 작성 (`src/domain/interfaces.py`의 `AIService` 구현)
  - `response_format` 인자를 활용하여 Pydantic 모델과 매핑
* **선행 작업**: [TASK-103], [TASK-201]
* **완료 조건**: API 호출 시 (네트워크 오류 제외) 정해진 스키마의 `AnalysisResult` 객체를 반환하거나 에러를 방출함
* **테스트 필요**: 예 (TDD 대상 - 외부 API Mocking 테스트)
* **결과 파일**: `src/infrastructure/openai_client.py`, `tests/integration/test_openai_client.py`

### [TASK-203] 오답 분석 비즈니스 서비스 (Application) (완료)
* **목적**: 라우터와 AI 인프라 사이의 브릿지 역할을 하는 서비스 로직
* **세부 작업**:
  - 프롬프트를 구성하고 AI 객체를 호출하여 결과를 병합 및 리턴하는 `AnalysisService` 구현
  - 외부 문제(Rate Limit, API Key 등) 시의 예외(Exception) 통일 처리
* **선행 작업**: [TASK-101], [TASK-201], [TASK-202]
* **완료 조건**: `AnalyzeRequest`를 받아 `AnalysisResult`를 성공적으로 반환하는 Service Layer가 완성됨
* **테스트 필요**: 예 (TDD 대상 - OpenAI 모방(Fake/Mock)을 사용한 서비스 계층 테스트)
* **결과 파일**: `src/application/services.py`, `tests/unit/test_services.py`

---

## Phase 3. 오답 저장 및 조회

### [TASK-301] 데이터베이스 환경 및 ORM 모델 구성
* **목적**: 분석이 완료된 노트를 저장하기 위한 DB 테이블 구성 (우선 SQLite)
* **세부 작업**:
  - `SQLAlchemy` 설정 및 엔진, 세션 팩토리 구성
  - `Note` 엔티티 매핑 스키마 작성(JSON 자료형 컬럼 포함)
* **선행 작업**: [TASK-101]
* **완료 조건**: DB 엔진 생성 및 `metadata.create_all()` 실행 시 테이블이 정상적으로 생성됨
* **테스트 필요**: 아니오 (설정의 영역에 해당)
* **결과 파일**: `src/infrastructure/database.py`

### [TASK-302] Note Repository 구현
* **목적**: 오답 노트를 DB에 저장하고, 조건별로 조회하는 데이터 접근 로직 구현
* **세부 작업**:
  - `NoteRepository` 인터페이스를 상속받은 `SQLAlchemyNoteRepository` 구현
  - `save(note)`, `get_all(filters)`, `get_by_id(note_id)`, `delete(note_id)` 구현
* **선행 작업**: [TASK-103], [TASK-301]
* **완료 조건**: InMemory SQLite 환경에서 CRUD 로직이 완벽하게 통과함
* **테스트 필요**: 예 (TDD 대상 - 저장 및 조회 로직)
* **결과 파일**: `src/infrastructure/sqlite_repository.py`, `tests/integration/test_repository.py`

### [TASK-303] 분석 엔드포인트(POST /analyze) 구축
* **목적**: 클라이언트로부터 분석 요청을 승인 및 처리하는 단일 API 라우터
* **세부 작업**:
  - `POST /api/v1/analyze` 라우터 구현
  - Dependency Injection을 활용한 의존성(Service, Repository) 주입
* **선행 작업**: [TASK-203], [TASK-302]
* **완료 조건**: `TestClient`로 Payload 주입 시 200 OK와 AI 결과 JSON이 반환됨 
* **테스트 필요**: 예 (통합 테스트)
* **결과 파일**: `src/presentation/api.py`, `tests/integration/test_api_analyze.py`

### [TASK-304] 노트 CRUD 엔드포인트(GET, DELETE /notes) 구축
* **목적**: 분석이 끝난 과거 노트 데이터에 접근하기 위한 API
* **세부 작업**:
  - `GET /api/v1/notes`, `GET /api/v1/notes/{id}`, `DELETE /api/v1/notes/{id}`
* **선행 작업**: [TASK-302], [TASK-303]
* **완료 조건**: 노트를 조회하고 정상적으로 삭제(HTTP 204)할 수 있음
* **테스트 필요**: 예 (통합 테스트)
* **결과 파일**: `src/presentation/api.py`, `tests/integration/test_api_notes.py`

---

## Phase 4. UI 개발 (React / Streamlit 검토)

> **알림**: UI 작업은 브라우저 렌더링, 시각 디자인 등에 강하게 결합하므로 자동화 테스트(TDD) 대상에서 제외하고 주로 수동 테스트(Manual Test)를 수행합니다.

### [TASK-401] 메인 대시보드 및 네비게이션 연결
* **목적**: 앱의 진입점과 기본 레이아웃 구성
* **세부 작업**:
  - 상단 컴포넌트 헤더, 사이드바/상단메뉴 연동
  - 레이아웃 구성 및 대시보드 껍데기(Skeleton) 완성
* **선행 작업**: 없음
* **완료 조건**: 모든 탭 이동 시 페이지 레이아웃이 깨지지 않아야 함
* **테스트 필요**: 아니오

### [TASK-402] 오답 분석 입력 폼 UI 및 API 연동
* **목적**: 사용자가 문제 텍스트와 선택지를 입력하고 API를 호출하는 뷰 구현
* **세부 작업**:
  - 폼 스테이트(State) 관리, 빈 텍스트 경고 등 클라이언트 검증 추가
  - `POST /api/v1/analyze` 백엔드 연동 및 로딩(Spinner) 상태 표시
* **선행 작업**: [TASK-303]
* **완료 조건**: 폼을 작성하고 "분석 시작" 클릭 시 완료 후 Analysis Result 화면으로 상태가 전이됨
* **테스트 필요**: 아니오

### [TASK-403] 분석 결과 시각화(Analysis Result) UI 구현
* **목적**: AI 분석 결과 전문을 시각적 카드로 렌더링
* **세부 작업**:
  - `AnalysisResult` 화면 바인딩 (`errorCategory` 스타일 및 정답/오답 사유 표시)
  - 핵심 학습 포인트 및 어휘 테이블 렌더링
* **선행 작업**: [TASK-402]
* **완료 조건**: 특정 ID 접속 시(또는 성공 후) 결과 카드가 전부 깨짐 없이 표출됨
* **테스트 필요**: 아니오

### [TASK-404] 오답 기록 리스트(Notes History) UI 구현
* **목적**: 과거 기록을 필터링 및 조회할 수 있는 리스트 페이지
* **세부 작업**:
  - `NotesHistory` 리스트 컴포넌트 
  - 카테고리/날짜 필터 및 페이지네이션 로직 연동
* **선행 작업**: [TASK-304], [TASK-403]
* **완료 조건**: 리스트 화면에서 필터 적용 시 뷰가 제대로 업데이트됨
* **테스트 필요**: 아니오

---

## Phase 5. 통계 및 대시보드

### [TASK-501] 통계 API 엔드포인트(`GET /stats`) 작성
* **목적**: 오답 내역에서 Part별, Category별 에러 횟수를 쿼리하는 백엔드 로직
* **세부 작업**:
  - DB Repository에 `.group_by()` 등 집계 쿼리 추가
  - `GET /api/v1/stats/summary` 라우터 추가
* **선행 작업**: [TASK-304]
* **완료 조건**: API 호출 시 취약 유형 비율과 최근 30일 동향 데이터가 반환됨
* **테스트 필요**: 예 (TDD 대상 - 통계 집계 정합성)
* **결과 파일**: `src/presentation/api.py`, `src/application/stats_service.py`

### [TASK-502] Weakness Dashboard UI 구현
* **목적**: 반환된 통계 데이터를 차트로 시각화
* **세부 작업**:
  - 바 차트, 파이 차트를 활용한 약점 분석 렌더링
* **선행 작업**: [TASK-501]
* **완료 조건**: 사용자의 오답 데이터에 비례하여 정확한 비율의 차트가 표출됨
* **테스트 필요**: 아니오

---

## Phase 6. 배포

### [TASK-601] 환경 변수 및 CORS 보안 설정
* **목적**: 보안 위협 제거 및 프로덕션 통신 허가
* **세부 작업**:
  - FastAPI `CORSMiddleware` 설정(프로덕트 도메인만 Allowed) 
  - API Rate Limit 방어 로직 검증 
* **선행 작업**: 전체 백엔드 개발
* **완료 조건**: 화이트리스트 외의 도메인에서 API 접근이 CORS 오류로 차단됨
* **테스트 필요**: 아니오 (보안 및 환경 설정)
* **결과 파일**: `src/presentation/api.py`, `src/config/settings.py`

### [TASK-602] 배포 전 수동 QA 파이프라인 (E2E) 점검
* **목적**: 사용자 입장에서 전체 흐름이 완벽히 이어지는지 릴리즈 전 최종 검증
* **세부 작업**:
  - 입력 -> 로딩 -> 분석 결과 -> 노트 저장 -> 대시보드 통계 반영 의 흐름을 매뉴얼 순회
* **선행 작업**: [TASK-502], [TASK-601]
* **완료 조건**: 모든 기능 결함(Bug)이 보고되지 않음
* **테스트 필요**: 아니오 (수동 QA)

### [TASK-603] 프론트엔드 및 백엔드 프로덕션 배포 
* **목적**: 서버리스(Render, Vercel 등) 환경에 앱 라이브 배포
* **세부 작업**:
  - 배포 스크립트 작성 (`Procfile` 또는 `.yml`)
  - 환경변수 및 Secrets 인젝션 세팅
* **선행 작업**: [TASK-602]
* **완료 조건**: 외부 URL을 통해 접속할 경우 서비스가 정상 작동하며, API 키 유출이 없음
* **테스트 필요**: 아니오

---

## Phase 7. 문서화와 포트폴리오 정리

### [TASK-701] README.md 최종 업데이트
* **목적**: 오픈소스 / 포트폴리오 관점에서의 저장소 안내문 강화
* **세부 작업**:
  - 프로젝트 소개, 아키텍처 다이어그램 스크린샷 캡쳐
  - TDD, SOLID 접근 철학에 대한 개발자 의도 서술
* **선행 작업**: [TASK-603]
* **완료 조건**: 방문자가 기여(Contributing)하거나 작동 원리를 바로 이해할 수 있음
* **테스트 필요**: 아니오
* **결과 파일**: `README.md`

### [TASK-702] 배포 시뮬레이션 및 포트폴리오용 데모 녹화
* **목적**: 리뷰어나 채용 담당자에게 기능의 유용성을 증명하는 리소스 제작
* **세부 작업**:
  - 주요 기능 사용 과정 Demo Gif 생성
  - 엣지 케이스 및 실패 처리 모범 사례(Design Patterns) 해설 추가
* **선행 작업**: [TASK-701]
* **결과 파일**: `docs/images/demo.gif` 등 
