import json
import re
from src.domain.interfaces import LLMProvider


class FakeLLMProvider(LLMProvider):
    """
    Fake static/dynamic LLM provider for testing and development environments.
    Strictly conforms to the JSON schema defined in docs/ANALYSIS_GUIDE.md.
    """

    def __init__(self, stub_response: str | None = None) -> None:
        self.stub_response = stub_response
        self.call_count = 0
        self.last_system_prompt = None
        self.last_user_prompt = None

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates static or dynamic mock JSON response conforming to AnalysisResult.
        """
        self.call_count += 1
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt

        # If stub_response was explicitly provided, use it
        if self.stub_response is not None:
            return self.stub_response

        # Default fallback values
        part = 5
        test_type = "RC"
        question_text = "The company's ------- to the new market was successful."
        choices = {"A": "expand", "B": "expansion", "C": "expansive", "D": "expansively"}
        correct_choice = "B"
        user_choice = "C"

        # Regex to extract Test Type
        tt_match = re.search(r"- Test Type:\s*([A-Za-z]+)", user_prompt)
        if tt_match:
            test_type = tt_match.group(1).strip()

        # Regex to extract Part
        p_match = re.search(r"- Part:\s*(\d+)", user_prompt)
        if p_match:
            part = int(p_match.group(1).strip())

        # Regex to extract Question
        q_match = re.search(r"\[Question\]\n(.*?)\n\n\[Choices\]", user_prompt, re.DOTALL)
        if q_match:
            question_text = q_match.group(1).strip()

        # Regex to extract Choices
        c_match = re.search(r"\[Choices\]\n(\{.*?\})", user_prompt, re.DOTALL)
        if c_match:
            try:
                choices = json.loads(c_match.group(1))
            except Exception:
                pass

        # Regex to extract Correct Answer
        ca_match = re.search(r"- Correct Answer:\s*([A-D])", user_prompt)
        if ca_match:
            correct_choice = ca_match.group(1).strip()

        # Regex to extract User's Answer
        ua_match = re.search(r"- User's Answer \(Wrong\):\s*([A-D])", user_prompt)
        if ua_match:
            user_choice = ua_match.group(1).strip()

        correct_text = choices.get(correct_choice, "Unknown")
        user_text = choices.get(user_choice, "Unknown")

        # Construct translation choices
        translation_choices = {}
        for k, v in choices.items():
            translation_choices[k] = f"{v} (한국어 번역 예시)"

        # Set error category based on test_type / part
        primary_category = "PART_OF_SPEECH"
        if part == 7:
            primary_category = "EVIDENCE_FINDING"
        elif test_type == "LC":
            primary_category = "LISTENING"

        mock_payload = {
            "translation": {
                "question": f"{question_text} (한국어 해석 예시)",
                "choices": translation_choices
            },
            "correctAnswer": {
                "choice": correct_choice,
                "text": correct_text
            },
            "correctReason": {
                "summary": f"{correct_choice}가 정답인 이유 요약",
                "detail": f"이 문제는 Part {part} 유형입니다. 빈칸 주변 문맥에 따라 {correct_choice}({correct_text})가 오는 것이 가장 적합합니다.",
                "grammarRule": "소유격(명사's / 소유격 대명사) + 명사" if part == 5 or part == 6 else None
            },
            "wrongAnswerReason": {
                "selectedChoice": user_choice,
                "selectedText": user_text,
                "summary": f"{user_choice}를 선택하여 오답",
                "detail": f"선택지 {user_choice}({user_text})는 문법적 기능 불일치 혹은 문맥상 오해로 인해 이 위치에 적절한 정답이 될 수 없습니다."
            },
            "errorCategory": {
                "primary": primary_category,
                "secondary": None,
                "description": f"사용자가 고른 오답 {user_choice}와 정답 {correct_choice}의 관계를 통해 {primary_category} 오류로 진단됨."
            },
            "learningPoint": {
                "title": f"Part {part} 핵심 문제 유형 분석법",
                "explanation": f"Part {part} {primary_category} 관련 오류는 주요 출제 패턴 중 하나입니다.",
                "examples": [
                    {
                        "english": f"Example sentence related to {correct_text}.",
                        "korean": f"단어 {correct_text}와 관련된 예문 해석입니다."
                    },
                    {
                        "english": f"Another practical sentence showing {user_text} usage.",
                        "korean": f"단어 {user_text}의 올바른 쓰임새를 보여주는 예문입니다."
                    }
                ],
                "tip": "지문 전체를 다 읽기 전에 빈칸 주변의 구조적 어휘 단서를 먼저 확인하세요."
            },
            "vocabulary": [
                {
                    "word": correct_text,
                    "partOfSpeech": "noun" if "ion" in correct_text.lower() else "verb",
                    "meaning": f"{correct_text}의 한국어 의미",
                    "exampleSentence": f"Please refer to the usage of {correct_text} in this sentence."
                },
                {
                    "word": user_text,
                    "partOfSpeech": "adjective" if "ive" in user_text.lower() else "adverb",
                    "meaning": f"{user_text}의 한국어 의미",
                    "exampleSentence": f"This is an example sentence featuring {user_text}."
                }
            ],
            "confidence": {
                "score": 0.95,
                "reason": "FakeLLMProvider를 통한 시뮬레이션 결과로 정합성이 보장됨."
            },
            "disclaimer": "이 분석은 FakeLLMProvider(개발 및 테스트용 모의 모델)에 의해 생성된 마크업 결과입니다. 실제 API 연동이 필요할 경우 OpenAIProvider 설정을 활성화하십시오."
        }

        return json.dumps(mock_payload, ensure_ascii=False)
