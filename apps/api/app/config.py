from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Feste Italia"
    app_env: str = "development"
    app_secret: str = "change-me"
    database_url: str = "postgresql+psycopg://feste_user:feste_password@db:5432/feste_db"
    redis_url: str = "redis://redis:6379/0"
    geocoding_enabled: bool = True
    geocoding_max_requests_per_refresh: int = 25
    nominatim_url: str = "https://nominatim.openstreetmap.org/search"
    nominatim_user_agent: str = "FesteItalia/0.1 geocoder"
    nominatim_email: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
