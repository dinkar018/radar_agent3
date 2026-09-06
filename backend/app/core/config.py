import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.0-flash"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/radar_agent.db"
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    UPLOAD_DIR: str = "./data"
    MAX_EXECUTION_TIMEOUT: int = 120
    SANDBOX_TYPE: str = "docker"
    SANDBOX_IMAGE: str = "radar-sandbox:latest"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def KB_DIR(self) -> str:
        return os.path.join(self.UPLOAD_DIR, "knowledge_base")

    @property
    def PAPERS_DIR(self) -> str:
        return os.path.join(self.UPLOAD_DIR, "papers")

    @property
    def RADAR_DATA_DIR(self) -> str:
        return os.path.join(self.UPLOAD_DIR, "radar_data")

    @property
    def RESULTS_DIR(self) -> str:
        return os.path.join(self.UPLOAD_DIR, "results")

settings = Settings()
