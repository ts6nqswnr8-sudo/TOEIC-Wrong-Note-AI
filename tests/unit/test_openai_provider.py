import os
import pytest
from unittest.mock import AsyncMock, patch
from openai import OpenAIError, AuthenticationError, APITimeoutError
from src.infrastructure.openai_client import OpenAIProvider

@pytest.fixture
def clean_env():
    """테스트 실행 전 OPENAI_API_KEY 환경변수 임시 제거 및 복원"""
    old_key = os.environ.get("OPENAI_API_KEY")
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    yield
    if old_key is not None:
        os.environ["OPENAI_API_KEY"] = old_key

@pytest.mark.asyncio
async def test_openai_provider_success():
    """모의(Mock) AsyncOpenAI 클라이언트를 통해 정상 결과 텍스트가 반환되는가"""
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(message=AsyncMock(content='{"result": "mocked_success"}'))
    ]

    with patch("src.infrastructure.openai_client.AsyncOpenAI") as mock_client_class:
        mock_instance = mock_client_class.return_value
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(api_key="fake_key_inject")
        result = await provider.generate("System Prompt", "User Prompt")

        assert result == '{"result": "mocked_success"}'
        mock_instance.chat.completions.create.assert_called_once()

def test_openai_provider_missing_api_key(clean_env):
    """API key 및 환경변수가 부재한 상태로 호출될 때 ValueError 예외를 발생시키는지 검증"""
    with pytest.raises(ValueError) as excinfo:
        OpenAIProvider()
    assert "OPENAI_API_KEY is not set" in str(excinfo.value)

@pytest.mark.asyncio
async def test_openai_provider_timeout_exception():
    """타임아웃 오류(APITimeoutError)를 상위로 전송 제어하는지 검증"""
    with patch("src.infrastructure.openai_client.AsyncOpenAI") as mock_client_class:
        mock_instance = mock_client_class.return_value
        mock_instance.chat.completions.create = AsyncMock(
            side_effect=APITimeoutError(request=None)
        )

        provider = OpenAIProvider(api_key="fake_key")
        with pytest.raises(APITimeoutError):
            await provider.generate("System", "User")

@pytest.mark.asyncio
async def test_openai_provider_auth_failure_exception():
    """인증 오류(AuthenticationError) 시나리오 전파 검증"""
    with patch("src.infrastructure.openai_client.AsyncOpenAI") as mock_client_class:
        mock_instance = mock_client_class.return_value
        mock_instance.chat.completions.create = AsyncMock(
            side_effect=AuthenticationError(
                message="Invalid API Key Mock",
                response=AsyncMock(status_code=401),
                body=None
            )
        )

        provider = OpenAIProvider(api_key="error_key")
        with pytest.raises(AuthenticationError):
            await provider.generate("System", "User")
