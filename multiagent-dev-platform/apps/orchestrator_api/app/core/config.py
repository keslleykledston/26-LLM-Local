"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""

    # ━━━ ENVIRONMENT ━━━
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # ━━━ API ━━━
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_RELOAD: bool = Field(default=True, env="API_RELOAD")
    SECRET_KEY: str = Field(default="dev_secret_key_change_in_prod", env="SECRET_KEY")

    # ━━━ CORS ━━━
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS",
    )

    # ━━━ OLLAMA (Local LLM) ━━━
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    OLLAMA_MODEL: str = Field(default="llama3.1:latest", env="OLLAMA_MODEL")
    OLLAMA_EMBEDDING_MODEL: str = Field(default="nomic-embed-text", env="OLLAMA_EMBEDDING_MODEL")
    OLLAMA_TIMEOUT: int = Field(default=300, env="OLLAMA_TIMEOUT")

    # ━━━ QDRANT (Vector Database) ━━━
    QDRANT_URL: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME: str = Field(default="multiagent_memory", env="QDRANT_COLLECTION_NAME")
    QDRANT_VECTOR_SIZE: int = Field(default=768, env="QDRANT_VECTOR_SIZE")

    # ━━━ DATABASE (PostgreSQL) ━━━
    DATABASE_URL: str = Field(
        default="postgresql://multiagent:multiagent_dev_2024@localhost:5432/multiagent",
        env="DATABASE_URL",
    )

    # ━━━ SECURITY & POLICY ━━━
    OFFLINE_ONLY_MODE: bool = Field(default=False, env="OFFLINE_ONLY_MODE")
    REQUIRE_APPROVAL_FOR_EXTERNAL_AI: bool = Field(default=True, env="REQUIRE_APPROVAL_FOR_EXTERNAL_AI")
    CACHE_EXTERNAL_AI_RESPONSES: bool = Field(default=True, env="CACHE_EXTERNAL_AI_RESPONSES")
    LOG_ALL_EXTERNAL_AI_CALLS: bool = Field(default=True, env="LOG_ALL_EXTERNAL_AI_CALLS")
    MAX_EXTERNAL_AI_COST_PER_MISSION_USD: float = Field(
        default=5.00, env="MAX_EXTERNAL_AI_COST_PER_MISSION_USD"
    )

    # ━━━ ANTHROPIC (Claude) ━━━
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = Field(default="claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")
    ANTHROPIC_ENABLED: bool = Field(default=False, env="ANTHROPIC_ENABLED")
    ANTHROPIC_MAX_TOKENS_PER_DAY: int = Field(default=100000, env="ANTHROPIC_MAX_TOKENS_PER_DAY")

    # ━━━ OPENAI (ChatGPT) ━━━
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    OPENAI_ENABLED: bool = Field(default=False, env="OPENAI_ENABLED")
    OPENAI_MAX_TOKENS_PER_DAY: int = Field(default=100000, env="OPENAI_MAX_TOKENS_PER_DAY")

    # ━━━ GOOGLE (Gemini) ━━━
    GOOGLE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    GOOGLE_MODEL: str = Field(default="gemini-pro", env="GOOGLE_MODEL")
    GOOGLE_ENABLED: bool = Field(default=False, env="GOOGLE_ENABLED")
    GOOGLE_MAX_TOKENS_PER_DAY: int = Field(default=100000, env="GOOGLE_MAX_TOKENS_PER_DAY")

    # ━━━ OPENROUTER ━━━
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = Field(default="anthropic/claude-3-opus", env="OPENROUTER_MODEL")
    OPENROUTER_ENABLED: bool = Field(default=False, env="OPENROUTER_ENABLED")
    OPENROUTER_MAX_TOKENS_PER_DAY: int = Field(default=50000, env="OPENROUTER_MAX_TOKENS_PER_DAY")

    # ━━━ PATHS ━━━
    @property
    def MEMORY_PATH(self) -> Path:
        return Path(__file__).parent.parent.parent.parent / "memory"

    @property
    def EXTERNAL_AI_PATH(self) -> Path:
        return Path(__file__).parent.parent.parent.parent / "external_ai"

    @property
    def PACKAGES_PATH(self) -> Path:
        return Path(__file__).parent.parent.parent.parent / "packages"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
