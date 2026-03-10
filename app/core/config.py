from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Tow Dispatch SaaS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    OPENAI_API_KEY: str | None = None

    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_PHONE_NUMBER: str | None = None

    GOOGLE_MAPS_API_KEY: str | None = None
    GOOGLE_ROUTES_TRAFFIC_AWARE: bool = True

    DATABASE_URL: str = "sqlite:///./ai_tow_saas.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()