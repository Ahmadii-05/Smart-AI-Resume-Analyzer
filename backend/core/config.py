from pydantic_settings import BaseSettings
from typing import List
import os, json

class Settings(BaseSettings):
    APP_NAME: str = "Smart AI Resume Analyzer"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    SECRET_KEY: str = "change-this-in-production"
    API_V1_PREFIX: str = "/api/v1"

    # Set this on Render as: '["https://your-frontend.onrender.com"]'
    ALLOWED_ORIGINS_STR: str = '["*"]'

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        try:
            return json.loads(self.ALLOWED_ORIGINS_STR)
        except Exception:
            return ["*"]

    DATABASE_URL: str = ""
    UPLOAD_DIR: str = "/tmp/uploads"
    OUTPUT_DIR: str = "/tmp/outputs"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx"]
    SPACY_MODEL: str = "en_core_web_sm"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()