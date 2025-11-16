from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "CubePython"
    version: str = "0.1.0"

    # CORS Settings
    backend_cors_origins: list[str] = ["http://localhost:3000"]

    # Database Settings
    database_url: str = "sqlite+aiosqlite:///./cubepython.db"

    # External API Settings
    scryfall_api_url: str = "https://api.scryfall.com"

    class Config:
        case_sensitive = True


settings = Settings()
