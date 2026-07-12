import os
from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"  # e.g., development, testing, production
    LLM_PROVIDER: str = "fake"    # e.g., fake, openai
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    DATABASE_URL: str = "sqlite:///./notes.db"

    @model_validator(mode="after")
    def validate_provider_and_key(self) -> 'AppSettings':
        # 1. APP_ENV=production일 경우, 반드시 LLM_PROVIDER는 openai여야 함
        if self.APP_ENV == "production" and self.LLM_PROVIDER != "openai":
            raise ValueError(
                "When APP_ENV is 'production', LLM_PROVIDER must be set to 'openai'."
            )

        # 2. LLM_PROVIDER=openai일 때 OPENAI_API_KEY 필수 검증
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER is set to 'openai'."
            )

        return self


# 싱글톤 설정 인스턴스 제공
settings = AppSettings()
