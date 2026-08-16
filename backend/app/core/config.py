"""
Semester OS — FastAPI Backend
Core application configuration and settings.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
import json


class Settings(BaseSettings):
    APP_NAME: str = "Semester OS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # JWT
    SECRET_KEY: str = "change-this-to-a-long-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./semester_os.db"

    # AI Configuration — Multi-Key Groq Engine
    AI_PROVIDER: str = "groq"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    AI_MODEL: str = "llama-3.3-70b-versatile"

    # Dedicated 5-Key Slot Configuration
    GROQ_API_KEY_1: Optional[str] = None
    GROQ_API_KEY_2: Optional[str] = None
    GROQ_API_KEY_3: Optional[str] = None
    GROQ_API_KEY_4: Optional[str] = None
    GROQ_API_KEY_5: Optional[str] = None

    # Fallback / Array Key Configurations
    GROQ_API_KEY: Optional[str] = None
    GROQ_API_KEYS: List[str] = []

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return ["*"]
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            # Comma-separated string support
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return ["*"]

    def get_groq_keys(self) -> List[str]:
        """
        Collect and deduplicate all valid configured Groq API keys across:
        1. Dedicated slots GROQ_API_KEY_1 .. GROQ_API_KEY_5
        2. Array GROQ_API_KEYS
        3. Single GROQ_API_KEY
        Returns only valid, non-empty, stripped keys.
        """
        raw_keys: List[str] = []

        # 1. Dedicated slot keys
        for key_slot in [
            self.GROQ_API_KEY_1,
            self.GROQ_API_KEY_2,
            self.GROQ_API_KEY_3,
            self.GROQ_API_KEY_4,
            self.GROQ_API_KEY_5,
        ]:
            if key_slot and isinstance(key_slot, str) and len(key_slot.strip()) > 8:
                raw_keys.append(key_slot.strip())

        # 2. Array keys
        if self.GROQ_API_KEYS:
            for k in self.GROQ_API_KEYS:
                if k and isinstance(k, str) and len(k.strip()) > 8:
                    raw_keys.append(k.strip())

        # 3. Single key fallback
        if self.GROQ_API_KEY and isinstance(self.GROQ_API_KEY, str) and len(self.GROQ_API_KEY.strip()) > 8:
            raw_keys.append(self.GROQ_API_KEY.strip())

        # Deduplicate preserving order
        seen = set()
        deduped = []
        for k in raw_keys:
            if k not in seen:
                seen.add(k)
                deduped.append(k)

        return deduped

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
