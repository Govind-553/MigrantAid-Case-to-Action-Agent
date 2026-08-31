import logging
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    LLM_API_KEY: str = Field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    LLM_MODEL: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gemini-3.6-flash"))
    DATABASE_URL: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    DIRECT_URL: str = Field(default_factory=lambda: os.getenv("DIRECT_URL", ""))
    APP_ENV: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    FRONTEND_URL: str = Field(default_factory=lambda: os.getenv("FRONTEND_URL", ""))

    @property
    def is_development(self) -> bool:
        return self.APP_ENV.lower() == "development"

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV.lower() == "testing"

    @property
    def allowed_origins(self) -> list[str]:
        """Explicit allowed origins for CORS.

        - If FRONTEND_URL is set, use its comma-separated values (production).
        - Otherwise default to the local dev frontend origins.
        A wildcard is never used while credentials are enabled.
        """
        if self.FRONTEND_URL:
            origins = [o.strip() for o in self.FRONTEND_URL.split(",") if o.strip()]
            if origins:
                return origins
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

settings = Settings()

# Setup logging configuration
logging_level = logging.DEBUG if settings.is_development else logging.INFO
logging.basicConfig(
    level=logging_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("migrantaid")
logger.info(f"Loaded configuration for environment: {settings.APP_ENV}")
