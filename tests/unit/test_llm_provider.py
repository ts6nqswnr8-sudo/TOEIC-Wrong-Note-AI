import pytest
from src.domain.interfaces import LLMProvider

class FakeLLMProvider(LLMProvider):
    """테스트를 위한 Fake LLMProvider 오버라이딩 구현체"""
    def __init__(self, stub_response: str = "{}") -> None:
        self.stub_response = stub_response
        self.last_system_prompt = None
        self.last_user_prompt = None

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.stub_response

@pytest.mark.asyncio
async def test_fake_llm_provider_generate():
    """FakeLLMProvider가 LLMProvider 규격을 만족하고 사전 모방 데이터를 리턴하는지 검증"""
    fake = FakeLLMProvider(stub_response='{"mocked": true}')
    
    response = await fake.generate("System Rules", "User Input")
    
    assert response == '{"mocked": true}'
    assert fake.last_system_prompt == "System Rules"
    assert fake.last_user_prompt == "User Input"
