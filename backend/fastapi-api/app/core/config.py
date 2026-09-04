from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Any, Union
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "PropLedger API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "propledger"
    DB_POOL_MIN: int = 2
    DB_POOL_MAX: int = 20
    
    # JWT Security
    SECRET_KEY: str = "propledger-enterprise-secret-key-32-chars-long-secure!!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean == "*":
                return ["*"]
            if v_clean.startswith("[") and v_clean.endswith("]"):
                import json
                try:
                    parsed = json.loads(v_clean)
                    if isinstance(parsed, list):
                        return [str(x) for x in parsed]
                except Exception:
                    pass
            origins = [i.strip() for i in v_clean.split(",") if i.strip()]
            return origins if origins else ["*"]
        elif isinstance(v, (list, tuple)):
            return [str(x) for x in v] if v else ["*"]
        return ["*"]

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
