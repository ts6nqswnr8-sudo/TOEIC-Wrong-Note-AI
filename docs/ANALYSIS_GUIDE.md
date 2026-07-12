# TOEIC Wrong Note AI — 오답 분석 기준 가이드

> **버전**: 1.0.0  
> **최종 수정**: 2026-07-12  
> **목적**: AI가 오답을 분석할 때 사용하는 유형 분류 기준과 응답 스키마를 정의한다.

---

## 목차

1. [오답 유형 분류 체계](#1-오답-유형-분류-체계)
2. [유형별 상세 정의](#2-유형별-상세-정의)
3. [AI 응답 JSON 스키마](#3-ai-응답-json-스키마)
4. [프롬프트 연동 가이드](#4-프롬프트-연동-가이드)
5. [확장 및 버전 관리 원칙](#5-확장-및-버전-관리-원칙)

---

## 1. 오답 유형 분류 체계

### 1-1. 분류 계층 구조

오답 유형은 **대분류 → 소분류** 2단계 계층으로 관리한다.

| 대분류 | 소분류 (errorCategory) | 코드 |
|--------|------------------------|------|
| **문법 (Grammar)** | 품사 오류 | `PART_OF_SPEECH` |
| | 시제·태 오류 | `TENSE_VOICE` |
| | 수일치·대명사 오류 | `AGREEMENT_PRONOUN` |
| | 접속사·관계사 오류 | `CONNECTOR` |
| | 문장 구조 오류 | `SENTENCE_STRUCTURE` |
| **어휘 (Vocabulary)** | 어휘 혼동 | `VOCABULARY` |
| | 전치사·숙어 오류 | `PREPOSITION_IDIOM` |
| **독해 (Reading)** | 지문 근거 파악 실패 | `EVIDENCE_FINDING` |
| | 패러프레이징 오류 | `PARAPHRASING` |
| **청해 (Listening)** | 청취·발음 혼동 | `LISTENING` |
| **기타 (Other)** | 집중력·단순 실수 | `CARELESS_MISTAKE` |
| | 기타 | `OTHER` |

### 1-2. 토익 Part별 주요 오답 유형 매핑

| Part | 주 출제 영역 | 빈출 오답 유형 |
|------|-------------|---------------|
| Part 1 | 사진 묘사 | `LISTENING`, `VOCABULARY` |
| Part 2 | 질의응답 | `LISTENING`, `SENTENCE_STRUCTURE` |
| Part 3 | 짧은 대화 | `LISTENING`, `PARAPHRASING`, `EVIDENCE_FINDING` |
| Part 4 | 설명문 | `LISTENING`, `PARAPHRASING`, `EVIDENCE_FINDING` |
| Part 5 | 단문 빈칸 | `PART_OF_SPEECH`, `TENSE_VOICE`, `VOCABULARY`, `PREPOSITION_IDIOM` |
| Part 6 | 장문 빈칸 | `CONNECTOR`, `TENSE_VOICE`, `SENTENCE_STRUCTURE` |
| Part 7 | 독해 | `EVIDENCE_FINDING`, `PARAPHRASING`, `VOCABULARY` |

---

## 2. 유형별 상세 정의

---

### 2-1. 품사 오류 (`PART_OF_SPEECH`)

**정의**  
빈칸에 들어갈 단어의 품사(명사·동사·형용사·부사)를 잘못 판단하여 오답을 선택한 경우.

**판정 기준**  
- 선택지가 같은 어근의 다른 품사 파생형으로 구성되어 있다.
- 사용자가 고른 답과 정답이 품사만 다르고 어근이 같거나 유사하다.
- 문장 내 빈칸의 문법적 역할(주어·목적어·수식어 등)을 분석했을 때 다른 품사가 필요한 자리이다.

**대표 오답 사례**

```
문제: The company's ------- to the new market was successful.
(A) expand   (B) expansion   (C) expansive   (D) expansively

정답: (B) expansion (명사)
오답 선택: (C) expansive (형용사)
분석: 소유격('s) 뒤 + to 전치사 앞이므로 명사가 필요한 자리에 형용사를 선택.
```

**학습 조언**  
- **빈칸 앞뒤 품사 판별법을 익히세요**: 관사/소유격 + `___` → 명사, be동사/감각동사 + `___` → 형용사, 동사/형용사/부사 + `___` + 동사 → 부사.
- 자주 출제되는 접미사를 정리하세요: `-tion`, `-ment`, `-ness` (명사) / `-ive`, `-ful`, `-able` (형용사) / `-ly` (부사).
- 같은 어근의 품사 변형을 한 묶음으로 암기하세요.

---

### 2-2. 어휘 혼동 (`VOCABULARY`)

**정의**  
의미가 비슷하거나 형태가 유사한 단어를 혼동하여 문맥에 맞지 않는 어휘를 선택한 경우.

**판정 기준**  
- 선택지가 서로 다른 단어(같은 품사)로 구성되어 있다.
- 사용자가 고른 단어가 문맥상 어색하거나 의미가 통하지 않는다.
- 정답과 오답 사이에 의미·철자·발음상 혼동 가능성이 있다.

**대표 오답 사례**

```
문제: The manager ------- the employees for their outstanding performance.
(A) complained   (B) commended   (C) competed   (D) compensated

정답: (B) commended (칭찬했다)
오답 선택: (D) compensated (보상했다)
분석: 'commend(칭찬하다)'와 'compensate(보상하다)'의 의미를 구별하지 못함.
```

**학습 조언**  
- 혼동하기 쉬운 단어를 **대조 쌍(pair)**으로 정리하세요: `commend` vs `compensate`, `affect` vs `effect`.
- 단어를 **예문 맥락** 속에서 암기하면 의미 구별이 쉬워집니다.
- 토익 빈출 어휘 1000개를 우선 학습하세요.

---

### 2-3. 전치사·숙어 오류 (`PREPOSITION_IDIOM`)

**정의**  
특정 동사·형용사·명사와 함께 쓰이는 전치사를 잘못 선택하거나, 숙어·관용 표현을 알지 못해 틀린 경우.

**판정 기준**  
- 빈칸이 전치사 자리이거나 선택지에 전치사구/숙어가 포함되어 있다.
- 정답은 특정 표현과 결합하는 고정 전치사이다.
- 사용자가 고른 전치사가 해당 표현과 결합하지 않는 전치사이다.

**대표 오답 사례**

```
문제: The results are consistent ------- our expectations.
(A) to   (B) for   (C) with   (D) on

정답: (C) with → consistent with (~와 일치하는)
오답 선택: (A) to
분석: 'consistent with'라는 고정 전치사 결합을 모르고, 방향의 의미로 'to'를 선택.
```

**학습 조언**  
- 토익 빈출 **전치사 결합 표현**을 목록으로 정리하세요: `comply with`, `result in`, `account for`, `contribute to`.
- 전치사를 '해석'이 아닌 **덩어리(chunk)**로 암기하세요.
- 숙어는 문장 속에서 반복 노출하며 익히는 것이 가장 효과적입니다.

---

### 2-4. 문장 구조 오류 (`SENTENCE_STRUCTURE`)

**정의**  
문장의 구조적 패턴(도치, 병렬, 비교, 가정법 등)을 파악하지 못해 틀린 경우.

**판정 기준**  
- 문장이 도치·병렬·비교·가정법 등 특수 구문을 사용하고 있다.
- 사용자가 구문의 구조적 패턴을 인식하지 못하고 일반 문장처럼 해석했다.
- 정답 선택에 구문 구조 이해가 필수적이었다.

**대표 오답 사례**

```
문제: Not only ------- the report, but she also presented it to the board.
(A) she completed   (B) did she complete   (C) she did complete   (D) completing she

정답: (B) did she complete
오답 선택: (A) she completed
분석: 'Not only'로 시작하는 도치 구문에서 '조동사 + 주어 + 동사 원형' 어순이 필요함을 놓침.
```

**학습 조언**  
- **도치 구문 트리거**를 암기하세요: `Not only`, `Hardly`, `Never`, `Seldom`, `Only when`.
- 병렬 구조에서는 `and`, `or`, `but` 앞뒤의 품사·형태를 맞춰야 합니다.
- 문장 구조 유형별로 대표 예문 3개씩 정리하면 패턴 인식이 빨라집니다.

---

### 2-5. 시제·태 오류 (`TENSE_VOICE`)

**정의**  
동사의 시제(현재·과거·완료 등)나 태(능동·수동)를 잘못 판단하여 틀린 경우.

**판정 기준**  
- 선택지가 같은 동사의 다른 시제·태 형태로 구성되어 있다.
- 문장에 시제 단서(시간 부사, 접속사 등)가 있는데 이를 놓쳤다.
- 주어와 동사의 능동/수동 관계를 잘못 판단했다.

**대표 오답 사례**

```
문제: The proposal ------- by the committee before the deadline.
(A) reviewed   (B) was reviewed   (C) has reviewed   (D) reviewing

정답: (B) was reviewed (수동태 과거)
오답 선택: (A) reviewed (능동태 과거)
분석: 주어 'proposal'은 '검토를 당하는' 대상이므로 수동태가 필요하지만 능동태를 선택.
```

**학습 조언**  
- **주어가 행위자인지 대상인지** 먼저 판단하세요 → 행위자 = 능동, 대상 = 수동.
- 시간 부사 키워드를 정리하세요: `since/for` → 완료, `yesterday` → 과거, `by next week` → 미래완료.
- `have been + p.p.`(현재완료 수동) 같은 복합 시제를 공식처럼 암기하세요.

---

### 2-6. 수일치·대명사 오류 (`AGREEMENT_PRONOUN`)

**정의**  
주어-동사 수일치, 또는 대명사의 격·수·성을 잘못 선택하여 틀린 경우.

**판정 기준**  
- 선택지가 단수/복수 동사형, 또는 인칭대명사의 다른 격(주격·목적격·소유격·재귀)으로 구성되어 있다.
- 주어의 수(단수/복수)를 잘못 파악했다.
- 대명사가 가리키는 선행사를 잘못 판단했다.

**대표 오답 사례**

```
문제: Each of the employees ------- required to submit a report.
(A) are   (B) is   (C) were   (D) have been

정답: (B) is
오답 선택: (A) are
분석: 'Each'가 단수 취급임을 놓지고, 'of the employees(복수)'에 이끌려 복수 동사 선택.
```

**학습 조언**  
- **단수 취급 키워드**를 암기하세요: `each`, `every`, `either`, `neither`, `anyone`, `someone`.
- 전치사구(`of the employees`)는 수일치 판단에서 무시하고, 진짜 주어만 보세요.
- 대명사 문제는 **선행사 찾기 → 수/격 결정** 순서로 풀으세요.

---

### 2-7. 접속사·관계사 오류 (`CONNECTOR`)

**정의**  
절과 절을 연결하는 접속사(등위·종속)나 관계대명사·관계부사를 잘못 선택한 경우.

**판정 기준**  
- 선택지가 접속사, 관계사, 접속부사 등으로 구성되어 있다.
- 빈칸 앞뒤 절의 논리적 관계(인과·양보·조건·시간 등)를 잘못 판단했다.
- 관계사의 선행사 종류(사람/사물/장소/이유)를 잘못 판단했다.

**대표 오답 사례**

```
문제: The event was postponed ------- the severe weather conditions.
(A) because   (B) due to   (C) although   (D) despite

정답: (B) due to (전치사구 → 뒤에 명사구)
오답 선택: (A) because (접속사 → 뒤에 절이 필요)
분석: 'because' 뒤에는 주어+동사가 있는 절이 와야 하는데, 뒤에 명사구만 있는 구조를 놓침.
```

**학습 조언**  
- **접속사 vs 전치사** 구분이 핵심입니다: `because` + 절 vs `because of` + 명사구, `although` + 절 vs `despite` + 명사구.
- 관계대명사는 선행사와 빈칸 뒤 문장의 빠진 성분을 확인하세요.
- Part 6에서 문맥 접속부사 문제가 자주 출제됩니다: `however`, `therefore`, `moreover`, `instead`.

---

### 2-8. 지문 근거 파악 실패 (`EVIDENCE_FINDING`)

**정의**  
지문(본문)에 근거가 명시되어 있는데 이를 찾지 못하거나, 지문에 없는 정보를 근거로 답을 선택한 경우.

**판정 기준**  
- Part 7(독해) 또는 Part 3·4(청해) 문제이다.
- 정답의 근거가 지문의 특정 문장/구절에 있는데 사용자가 이를 놓쳤다.
- 사용자가 지문 밖의 배경지식이나 상식에 기반하여 오답을 선택했다.

**대표 오답 사례**

```
문제: What is indicated about the new policy?
지문: "The revised policy will take effect starting January 1 and applies 
      to all full-time employees in the marketing department."

정답: (C) It applies only to certain employees.
오답 선택: (A) It applies to all company employees.
분석: 'all full-time employees in the marketing department'를 'all employees'로 
     확대 해석하여 지문의 한정 조건을 놓침.
```

**학습 조언**  
- 선택지를 먼저 읽고 **키워드를 지문에서 위치 확인(scanning)** 하는 습관을 기르세요.
- "all", "only", "always", "never" 같은 **극단적 표현**이 있는 선택지는 주의하세요.
- 답은 반드시 **지문 안에** 있습니다. 상식으로 판단하지 마세요.

---

### 2-9. 패러프레이징 오류 (`PARAPHRASING`)

**정의**  
지문의 표현이 선택지에서 다른 단어/구문으로 바꿔 표현(paraphrase)된 것을 인식하지 못해 틀린 경우.

**판정 기준**  
- 정답 선택지가 지문의 내용을 다른 표현으로 바꿔 쓴 것이다.
- 사용자가 지문의 원문 표현과 똑같은 단어가 들어간 오답(함정 선택지)을 골랐다.
- 동의어·유의어 변환을 인식하지 못한 것이 오답 원인이다.

**대표 오답 사례**

```
문제: What does the speaker suggest?
지문 (음성): "I think we should put off the meeting until next week."

정답: (B) The meeting should be postponed.
오답 선택: (D) The meeting should be held next week as originally planned.
분석: 'put off(연기하다) = postpone'라는 패러프레이징을 놓치고,
     'next week'라는 표면적 키워드에 이끌려 함정 선택지를 골랐다.
```

**학습 조언**  
- 토익 빈출 **패러프레이징 쌍**을 정리하세요: `put off = postpone`, `look into = investigate`, `get in touch with = contact`.
- 선택지에 지문과 **똑같은 단어**가 있으면 오히려 함정일 가능성을 의심하세요.
- 구동사(phrasal verb)와 그 동의어를 함께 학습하면 효과적입니다.

---

### 2-10. 청취·발음 혼동 (`LISTENING`)

**정의**  
발음이 비슷한 단어를 혼동하거나, 음성을 정확히 듣지 못해 틀린 경우. (Part 1~4)

**판정 기준**  
- Listening 파트 문제이다.
- 오답 선택지의 단어가 정답 또는 음성 내용과 **발음이 유사**하다.
- 연음·축약·강세 패턴을 인식하지 못한 것이 오답 원인이다.

**대표 오답 사례**

```
문제: (Part 2 음성) "When will the shipment arrive?"
(A) It's on the second shelf.  
(B) By Thursday at the latest.  
(C) Yes, the shift starts at nine.

정답: (B) By Thursday at the latest.
오답 선택: (C) Yes, the shift starts at nine.
분석: 'shipment'와 'shift'의 발음 유사성에 혼동.
     'When' 의문사 질문에 'Yes'로 답하는 것이 부자연스러움을 놓침.
```

**학습 조언**  
- **의문사 유형 판별**을 최우선으로 하세요: `When` → 시간, `Where` → 장소, `Who` → 사람. Yes/No로 대답할 수 없습니다.
- 토익 빈출 **음성 함정 쌍**을 정리하세요: `copy/coffee`, `work/walk`, `right/light`.
- 음성을 들을 때 **첫 단어(의문사/주어)**에 집중하세요.

---

### 2-11. 집중력·단순 실수 (`CARELESS_MISTAKE`)

**정의**  
문법·어휘 지식은 충분하지만 시간 부족, 부주의, 마킹 실수 등으로 틀린 경우.

**판정 기준**  
- 사용자가 해당 유형의 문제를 평소에 정확히 풀 수 있는 수준이라고 자가 진단한다.
- 오답 원인이 지식 부족이 아닌 **실행 오류**(안 읽음, 급하게 풀음, 마킹 착오)이다.
- AI가 분석했을 때 오답에 특별한 지식 결함 패턴이 보이지 않는다.

> ⚠️ **주의**: 이 유형은 AI가 자동 판정하기 어렵다. 사용자가 "이 문제는 알고 있었는데 실수로 틀렸다"고 표시할 수 있는 오버라이드 기능을 UI에 제공한다.

**대표 오답 사례**

```
문제: All documents must be submitted ------- Friday.
(A) by   (B) until   (C) for   (D) since

정답: (A) by
오답 선택: (A) by ← 실제로는 마킹을 (B)에 함
분석: 정답을 알고 있었으나 OMR 마킹 시 한 칸 밀려 (B)를 표기.
```

**학습 조언**  
- 시간 관리를 연습하세요: Part 5는 문제당 **20~30초**, Part 7은 **1분 내외**.
- 마킹은 **5문제씩 모아서** 하면 실수를 줄일 수 있습니다.
- 어려운 문제는 과감히 **건너뛰고** 나중에 돌아오세요.

---

### 2-12. 기타 (`OTHER`)

**정의**  
위 11개 유형 어디에도 해당하지 않거나, 복합적 원인으로 분류가 모호한 경우.

**판정 기준**  
- 위 유형 중 어느 하나에도 확신 있게 분류할 수 없다.
- 두 가지 이상의 유형이 복합적으로 작용하여 하나로 특정이 어렵다.
- 문제 자체가 비정형이거나 분류 체계에 없는 새로운 패턴이다.

**대표 오답 사례**

```
여러 유형이 복합적으로 작용하는 경우:
- 어휘를 몰라서(VOCABULARY) 문장 구조도 파악하지 못한(SENTENCE_STRUCTURE) 경우
- 지문 근거를 찾았지만(EVIDENCE_FINDING) 패러프레이징을 놓친(PARAPHRASING) 경우
```

**학습 조언**  
- 복합 오류인 경우, 가장 근본적인 원인 하나를 골라 집중 학습하세요.
- 이 유형이 누적되면 분류 기준을 재검토할 필요가 있습니다.

---

## 3. AI 응답 JSON 스키마

### 3-1. 전체 스키마

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TOEIC Wrong Note Analysis Response",
  "description": "AI가 토익 오답을 분석한 결과를 반환하는 JSON 구조",
  "type": "object",
  "required": [
    "translation",
    "correctAnswer",
    "correctReason",
    "wrongAnswerReason",
    "errorCategory",
    "learningPoint",
    "vocabulary",
    "confidence",
    "disclaimer"
  ],
  "properties": {
    "translation": {
      "type": "object",
      "description": "문제 본문과 선택지의 한국어 해석",
      "required": ["question", "choices"],
      "properties": {
        "question": {
          "type": "string",
          "description": "문제 본문 한국어 해석"
        },
        "choices": {
          "type": "object",
          "description": "각 선택지의 한국어 해석",
          "required": ["A", "B", "C", "D"],
          "properties": {
            "A": { "type": "string" },
            "B": { "type": "string" },
            "C": { "type": "string" },
            "D": { "type": "string" }
          }
        }
      }
    },
    "correctAnswer": {
      "type": "object",
      "description": "정답 정보",
      "required": ["choice", "text"],
      "properties": {
        "choice": {
          "type": "string",
          "enum": ["A", "B", "C", "D"],
          "description": "정답 선택지 기호"
        },
        "text": {
          "type": "string",
          "description": "정답 선택지 텍스트"
        }
      }
    },
    "correctReason": {
      "type": "object",
      "description": "정답인 이유에 대한 상세 설명",
      "required": ["summary", "detail", "grammarRule"],
      "properties": {
        "summary": {
          "type": "string",
          "description": "정답 근거 한 줄 요약 (30자 이내)"
        },
        "detail": {
          "type": "string",
          "description": "정답 근거 상세 설명 (문법·어휘·문맥 근거 포함)"
        },
        "grammarRule": {
          "type": ["string", "null"],
          "description": "관련 문법 규칙명 (해당 시). 어휘 문제 등 문법 규칙이 없으면 null."
        }
      }
    },
    "wrongAnswerReason": {
      "type": "object",
      "description": "사용자가 고른 오답이 틀린 이유",
      "required": ["selectedChoice", "selectedText", "summary", "detail"],
      "properties": {
        "selectedChoice": {
          "type": "string",
          "enum": ["A", "B", "C", "D"],
          "description": "사용자가 선택한 오답 기호"
        },
        "selectedText": {
          "type": "string",
          "description": "사용자가 선택한 오답 텍스트"
        },
        "summary": {
          "type": "string",
          "description": "오답 이유 한 줄 요약 (30자 이내)"
        },
        "detail": {
          "type": "string",
          "description": "왜 이 선택지가 틀렸는지 구체적 설명"
        }
      }
    },
    "errorCategory": {
      "type": "object",
      "description": "오답 원인 분류",
      "required": ["primary", "description"],
      "properties": {
        "primary": {
          "type": "string",
          "enum": [
            "PART_OF_SPEECH",
            "VOCABULARY",
            "PREPOSITION_IDIOM",
            "SENTENCE_STRUCTURE",
            "TENSE_VOICE",
            "AGREEMENT_PRONOUN",
            "CONNECTOR",
            "EVIDENCE_FINDING",
            "PARAPHRASING",
            "LISTENING",
            "CARELESS_MISTAKE",
            "OTHER"
          ],
          "description": "주요 오답 원인 코드"
        },
        "secondary": {
          "type": ["string", "null"],
          "enum": [
            "PART_OF_SPEECH",
            "VOCABULARY",
            "PREPOSITION_IDIOM",
            "SENTENCE_STRUCTURE",
            "TENSE_VOICE",
            "AGREEMENT_PRONOUN",
            "CONNECTOR",
            "EVIDENCE_FINDING",
            "PARAPHRASING",
            "LISTENING",
            "CARELESS_MISTAKE",
            "OTHER",
            null
          ],
          "description": "보조 오답 원인 코드 (복합 원인일 때). 단일 원인이면 null."
        },
        "description": {
          "type": "string",
          "description": "이 문제에서 해당 유형으로 분류한 구체적 근거 설명"
        }
      }
    },
    "learningPoint": {
      "type": "object",
      "description": "복습할 학습 포인트",
      "required": ["title", "explanation", "examples", "tip"],
      "properties": {
        "title": {
          "type": "string",
          "description": "학습 포인트 제목 (예: '소유격 뒤 품사 판별법')"
        },
        "explanation": {
          "type": "string",
          "description": "핵심 개념 설명"
        },
        "examples": {
          "type": "array",
          "description": "관련 예문 목록 (2~3개)",
          "items": {
            "type": "object",
            "required": ["english", "korean"],
            "properties": {
              "english": {
                "type": "string",
                "description": "영어 예문"
              },
              "korean": {
                "type": "string",
                "description": "한국어 해석"
              }
            }
          },
          "minItems": 2,
          "maxItems": 3
        },
        "tip": {
          "type": "string",
          "description": "실전 풀이 팁 (한 줄)"
        }
      }
    },
    "vocabulary": {
      "type": "array",
      "description": "이 문제에서 학습할 핵심 어휘 목록",
      "items": {
        "type": "object",
        "required": ["word", "partOfSpeech", "meaning", "exampleSentence"],
        "properties": {
          "word": {
            "type": "string",
            "description": "영어 단어·표현"
          },
          "partOfSpeech": {
            "type": "string",
            "enum": ["noun", "verb", "adjective", "adverb", "preposition", "conjunction", "phrase"],
            "description": "품사"
          },
          "meaning": {
            "type": "string",
            "description": "한국어 뜻"
          },
          "exampleSentence": {
            "type": "string",
            "description": "예문"
          }
        }
      },
      "minItems": 1,
      "maxItems": 5
    },
    "confidence": {
      "type": "object",
      "description": "AI 분석의 신뢰도",
      "required": ["score", "reason"],
      "properties": {
        "score": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "신뢰도 점수 (0.0~1.0). 문제가 명확하고 분석 근거가 확실할수록 높음."
        },
        "reason": {
          "type": "string",
          "description": "신뢰도 판단 근거 (예: '선택지 구성이 명확하여 품사 문제로 확인됨')"
        }
      }
    },
    "disclaimer": {
      "type": "string",
      "description": "AI 분석의 한계를 알리는 면책 문구",
      "default": "이 분석은 AI가 생성한 것으로, 실제 출제 의도와 다를 수 있습니다. 참고 자료로 활용하시고, 정확한 해설은 공식 교재를 확인하세요."
    }
  }
}
```

### 3-2. 응답 예시

```json
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
    "summary": "소유격 뒤, 전치사 앞이므로 명사가 필요",
    "detail": "\"The company's\" 소유격 뒤에 위치하고, 뒤에 전치사 \"to\"가 오므로 이 자리에는 명사가 와야 합니다. 'expansion'은 'expand'의 명사형으로, '확장'이라는 의미를 가지며 문법적으로 주어 역할을 합니다.",
    "grammarRule": "소유격(명사's / 소유격 대명사) + 명사"
  },
  "wrongAnswerReason": {
    "selectedChoice": "C",
    "selectedText": "expansive",
    "summary": "형용사는 이 위치에서 주어 역할을 할 수 없음",
    "detail": "'expansive'는 형용사로 '광범위한, 확장적인'이라는 의미입니다. 소유격 뒤에 올 수는 있지만, 그 경우 뒤에 수식할 명사가 필요합니다(예: the company's expansive plan). 이 문장에서는 빈칸 뒤에 전치사 'to'가 바로 오므로, 빈칸 자체가 명사(주어)여야 합니다."
  },
  "errorCategory": {
    "primary": "PART_OF_SPEECH",
    "secondary": null,
    "description": "선택지가 동일 어근(expand)의 품사 변형이며, 소유격 뒤 명사 자리에 형용사를 선택한 전형적인 품사 판별 오류."
  },
  "learningPoint": {
    "title": "소유격 뒤 품사 판별법",
    "explanation": "소유격(my, his, the company's 등) 뒤에는 반드시 명사(구)가 옵니다. 소유격과 명사 사이에 형용사가 올 수 있지만, 빈칸 바로 뒤에 전치사·동사가 오면 빈칸에는 명사만 가능합니다.",
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
    },
    {
      "word": "expansive",
      "partOfSpeech": "adjective",
      "meaning": "광범위한, 확장적인",
      "exampleSentence": "The company has an expansive network of suppliers."
    },
    {
      "word": "expand",
      "partOfSpeech": "verb",
      "meaning": "확장하다, 넓히다",
      "exampleSentence": "We plan to expand our operations to Europe next year."
    }
  ],
  "confidence": {
    "score": 0.95,
    "reason": "선택지가 동일 어근의 품사 변형으로 구성된 전형적인 Part 5 품사 문제이며, 문장 구조가 명확하여 높은 신뢰도로 분석 가능."
  },
  "disclaimer": "이 분석은 AI가 생성한 것으로, 실제 출제 의도와 다를 수 있습니다. 참고 자료로 활용하시고, 정확한 해설은 공식 교재를 확인하세요."
}
```

---

## 4. 프롬프트 연동 가이드

### 4-1. 시스템 프롬프트에 포함할 분류 기준 요약

AI 프롬프트에 다음 분류 코드와 정의를 포함하여 일관된 분류가 이루어지도록 한다.

```
오답 유형 코드 목록:
- PART_OF_SPEECH: 품사(명사·동사·형용사·부사)를 잘못 판단
- VOCABULARY: 의미·형태가 유사한 어휘를 혼동
- PREPOSITION_IDIOM: 전치사 결합 또는 숙어·관용 표현 오류
- SENTENCE_STRUCTURE: 도치·병렬·비교·가정법 등 구문 구조 미파악
- TENSE_VOICE: 시제 또는 능동·수동태 판단 오류
- AGREEMENT_PRONOUN: 주어-동사 수일치 또는 대명사 격·수·성 오류
- CONNECTOR: 접속사·관계사·접속부사 선택 오류
- EVIDENCE_FINDING: 지문 내 근거를 찾지 못하거나 없는 정보로 판단
- PARAPHRASING: 동의어·다른 표현으로 바꿔 쓴 것을 인식 실패
- LISTENING: 발음 유사 단어 혼동 또는 음성 미청취 (Listening 파트만)
- CARELESS_MISTAKE: 지식은 있으나 부주의·시간 부족으로 인한 실수
- OTHER: 위 유형에 해당하지 않거나 복합적 원인
```

### 4-2. 분류 우선순위 규칙

AI가 여러 유형에 해당하는 경우 다음 규칙을 적용한다:

1. **가장 근본적인 원인**을 `primary`로 지정한다.
2. 부수적 원인이 있다면 `secondary`에 지정한다.
3. `CARELESS_MISTAKE`는 AI가 단독으로 판정하지 않고, confidence가 낮을 때만 후보로 제안한다.
4. `OTHER`는 다른 모든 유형을 검토한 후 마지막 수단으로만 사용한다.

### 4-3. confidence 점수 가이드

| 점수 범위 | 의미 | 예시 상황 |
|----------|------|----------|
| 0.9 ~ 1.0 | 매우 높음 | 선택지 구성·문장 구조가 명확한 전형적 문제 |
| 0.7 ~ 0.89 | 높음 | 분석 가능하나 약간의 해석 여지가 있음 |
| 0.5 ~ 0.69 | 보통 | 문제 정보 부족 또는 복합 유형 |
| 0.0 ~ 0.49 | 낮음 | 문제 텍스트 불명확, 오답 원인 특정 어려움 |

---

## 5. 확장 및 버전 관리 원칙

### 5-1. 새로운 오답 유형 추가 절차

1. 기존 `OTHER`로 분류된 오답 데이터를 주기적으로 분석한다.
2. 특정 패턴이 **10건 이상** 반복되면 새 유형 후보로 검토한다.
3. 새 유형 추가 시 이 문서의 다음 항목을 업데이트한다:
   - 분류 체계 테이블 (§1-1)
   - 유형별 상세 정의 (§2)
   - JSON 스키마의 `errorCategory.primary` enum 값
   - 프롬프트 분류 기준 (§4-1)
4. 스키마 버전을 올린다 (SemVer).

### 5-2. 스키마 버전 관리

| 변경 유형 | 버전 업 규칙 |
|----------|-------------|
| 필드 추가 (하위 호환) | Minor (1.0 → 1.1) |
| 필드 삭제·이름 변경 | Major (1.0 → 2.0) |
| 설명·예시만 수정 | Patch (1.0.0 → 1.0.1) |

### 5-3. 오답 유형 코드 상수 (구현 시 참조)

```javascript
// src/domain/constants/errorCategories.js

export const ERROR_CATEGORIES = Object.freeze({
  PART_OF_SPEECH:     { code: 'PART_OF_SPEECH',     label: '품사 오류',         group: 'GRAMMAR' },
  VOCABULARY:         { code: 'VOCABULARY',          label: '어휘 혼동',         group: 'VOCABULARY' },
  PREPOSITION_IDIOM:  { code: 'PREPOSITION_IDIOM',   label: '전치사·숙어 오류',  group: 'VOCABULARY' },
  SENTENCE_STRUCTURE: { code: 'SENTENCE_STRUCTURE',  label: '문장 구조 오류',    group: 'GRAMMAR' },
  TENSE_VOICE:        { code: 'TENSE_VOICE',         label: '시제·태 오류',      group: 'GRAMMAR' },
  AGREEMENT_PRONOUN:  { code: 'AGREEMENT_PRONOUN',   label: '수일치·대명사 오류', group: 'GRAMMAR' },
  CONNECTOR:          { code: 'CONNECTOR',           label: '접속사·관계사 오류', group: 'GRAMMAR' },
  EVIDENCE_FINDING:   { code: 'EVIDENCE_FINDING',    label: '지문 근거 파악 실패', group: 'READING' },
  PARAPHRASING:       { code: 'PARAPHRASING',        label: '패러프레이징 오류',  group: 'READING' },
  LISTENING:          { code: 'LISTENING',            label: '청취·발음 혼동',    group: 'LISTENING' },
  CARELESS_MISTAKE:   { code: 'CARELESS_MISTAKE',    label: '집중력·단순 실수',   group: 'OTHER' },
  OTHER:              { code: 'OTHER',               label: '기타',             group: 'OTHER' },
});

export const ERROR_GROUPS = Object.freeze({
  GRAMMAR:    { code: 'GRAMMAR',    label: '문법' },
  VOCABULARY: { code: 'VOCABULARY', label: '어휘' },
  READING:    { code: 'READING',    label: '독해' },
  LISTENING:  { code: 'LISTENING',  label: '청해' },
  OTHER:      { code: 'OTHER',     label: '기타' },
});
```

---

> **이 문서는 프로젝트의 분석 로직과 LLM 프롬프트의 기준 문서입니다.**  
> 오답 분류 기준이나 JSON 스키마를 변경할 때는 반드시 이 문서를 먼저 업데이트하세요.
