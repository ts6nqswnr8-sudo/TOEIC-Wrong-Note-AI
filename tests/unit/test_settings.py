import pytest
from pydantic import ValidationError
from src.config.settings import AppSettings


def test_settings_default():
    """Verify that default settings load as development and fake provider."""
    # Under test environment, we can instantiate AppSettings directly
    settings = AppSettings(APP_ENV="development", LLM_PROVIDER="fake")
    assert settings.APP_ENV == "development"
    assert settings.LLM_PROVIDER == "fake"


def test_settings_production_requires_openai():
    """Verify that production env requiresopenai provider."""
    with pytest.raises(ValidationError) as excinfo:
        AppSettings(APP_ENV="production", LLM_PROVIDER="fake")
    assert "When APP_ENV is 'production', LLM_PROVIDER must be set to 'openai'." in str(excinfo.value)


def test_settings_openai_requires_api_key():
    """Verify that openai provider requires API key."""
    with pytest.raises(ValidationError) as excinfo:
        AppSettings(APP_ENV="development", LLM_PROVIDER="openai", OPENAI_API_KEY="")
    assert "OPENAI_API_KEY is required when LLM_PROVIDER is set to 'openai'." in str(excinfo.value)


def test_settings_valid_openai_config():
    """Verify that valid configuration passes validation."""
    settings = AppSettings(
        APP_ENV="production",
        LLM_PROVIDER="openai",
        OPENAI_API_KEY="valid-api-key"
    )
    assert settings.APP_ENV == "production"
    assert settings.LLM_PROVIDER == "openai"
    assert settings.OPENAI_API_KEY == "valid-api-key"
