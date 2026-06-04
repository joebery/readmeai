from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://readmeai:readmeai@db:5432/readmeai"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    # OpenAI pricing (gpt-4o-mini, per 1M tokens)
    openai_input_cost_per_1m: float = 0.15
    openai_output_cost_per_1m: float = 0.60
    openai_estimated_output_tokens: int = 2000
    openai_model: str = "gpt-4o-mini"


settings = Settings()
