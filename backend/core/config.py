"""
Core configuration using Pydantic Settings
All environment variables are loaded here
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Smart AI Resume Analyzer"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
    ]

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/resume_analyzer"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx"]

    # AI Models
    SPACY_MODEL: str = "en_core_web_sm"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"

    # Anthropic (for LLM suggestions)
    ANTHROPIC_API_KEY: str = ""

    # Output
    OUTPUT_DIR: str = "./outputs"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
