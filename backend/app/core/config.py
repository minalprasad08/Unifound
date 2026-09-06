import os
from typing import List, Union, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "UniFound - AI-Powered Lost & Found Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    # Default to SQLite for seamless zero-setup local dev & test verification; PostgreSQL supported via DATABASE_URL
    DATABASE_URL: str = "sqlite:///./unifound.db"

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: str | None) -> str:
        if not v:
            return "sqlite:///./unifound.db"
        # Support cloud providers that use postgres:// instead of postgresql://
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    # Security & JWT
    SECRET_KEY: str = "unifound_super_secret_jwt_key_change_in_production_2026_xyz!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v: str, info) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long for cryptographic security.")
        # Detect environment from os.environ or values
        env = os.environ.get("ENVIRONMENT", "development").lower()
        insecure_keys = {
            "unifound_super_secret_jwt_key_change_in_production_2026_xyz!",
            "changethisinproduction",
            "secret",
            "your-secret-key",
            "12345678901234567890123456789012",
        }
        if env == "production" and v in insecure_keys:
            raise ValueError("Insecure default SECRET_KEY detected in production environment! You must set a strong unique SECRET_KEY in .env.")
        return v

    # Host & CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 10
    RATE_LIMIT_REGISTER_PER_MINUTE: int = 5
    RATE_LIMIT_AGENT_PER_MINUTE: int = 20
    RATE_LIMIT_UPLOAD_PER_MINUTE: int = 10
    RATE_LIMIT_CLAIM_PER_MINUTE: int = 15

    # Uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_FILE_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]

    # MCP (Model Context Protocol) Configuration
    MCP_ENABLED: bool = True
    MCP_SERVER_NAME: str = "unifound"
    MCP_SERVER_HOST: str = "127.0.0.1"
    MCP_SERVER_PORT: int = 8001
    MCP_REQUEST_TIMEOUT: int = 30

    # Agentic AI & LLM Gateway Configuration (Phase 11)
    LLM_PROVIDER: str = "heuristic"  # heuristic, gemini, openai
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_API_KEY: Optional[str] = None
    LLM_FALLBACK_PROVIDER: str = "heuristic"
    LLM_REQUEST_TIMEOUT: int = 15
    AGENT_MAX_ITERATIONS: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
