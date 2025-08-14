from typing import List, Union, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator
import os
from pathlib import Path
import warnings

class Settings(BaseSettings):
    # Pydantic v2 settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore',  # ignore unknown env vars to avoid crashing on extras
    )

    APP_NAME: str = "ApexADE"
    APP_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./apex_ade.db"
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 1073741824  # 1GB - supports large PDFs (900MB+)
    UPLOAD_DIRECTORY: str = "./uploads"
    
    # ------------------------------------------------------------------
    # Storage configuration
    # ------------------------------------------------------------------
    # Select where uploaded files are placed before processing:
    #   - "local" (default): save to local filesystem (UPLOAD_DIRECTORY)
    #   - "azure":  upload directly to Azure Blob Storage via SAS URL
    STORAGE_MODE: str = "local"

    # Azure Blob Storage settings (used when STORAGE_MODE == "azure")
    AZURE_STORAGE_ACCOUNT_NAME: str = ""
    AZURE_STORAGE_ACCOUNT_KEY: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = ""
    # Minutes before an issued SAS token expires
    AZURE_SAS_TTL_MINUTES: int = 60

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[Union[AnyHttpUrl, str]] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Landing.ai SDK
    VISION_AGENT_API_KEY: str = ""
    
    # OpenAI GPT-5 settings (latest model as of August 2025)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5"  # GPT-5 is the latest model (released August 2025)
    OPENAI_MAX_COMPLETION_TOKENS: int = 8192  # Max tokens for GPT-5 responses
    OPENAI_VERBOSITY: str = "medium"  # low, medium, or high - controls response length
    OPENAI_REASONING_EFFORT: str = "medium"  # minimal, low, medium, or high
    OPENAI_TEMPERATURE: float = 0.1  # Lower temperature for more accurate document analysis

    # Backwards-compatibility: accept deprecated OPENAI_MAX_TOKENS env var
    # NOTE: OPENAI_MAX_TOKENS is deprecated in favor of OPENAI_MAX_COMPLETION_TOKENS
    # Precedence: OPENAI_MAX_COMPLETION_TOKENS > OPENAI_MAX_TOKENS (if both are set)
    OPENAI_MAX_TOKENS: Optional[int] = None

    def __init__(self, **values):
        super().__init__(**values)
        
        # Handle deprecated OPENAI_MAX_TOKENS with clear precedence rules
        if self.OPENAI_MAX_TOKENS is not None:
            # Get the original value of OPENAI_MAX_COMPLETION_TOKENS before any modifications
            original_max_completion = values.get('OPENAI_MAX_COMPLETION_TOKENS', 8192)
            
            # Check if OPENAI_MAX_COMPLETION_TOKENS was explicitly set (not just default)
            if 'OPENAI_MAX_COMPLETION_TOKENS' in os.environ:
                # OPENAI_MAX_COMPLETION_TOKENS takes precedence when both are set
                warnings.warn(
                    f"Both OPENAI_MAX_TOKENS and OPENAI_MAX_COMPLETION_TOKENS are set in environment. "
                    f"Using OPENAI_MAX_COMPLETION_TOKENS={self.OPENAI_MAX_COMPLETION_TOKENS}. "
                    f"Please remove the deprecated OPENAI_MAX_TOKENS from your configuration.",
                    DeprecationWarning,
                    stacklevel=2
                )
            else:
                # Only OPENAI_MAX_TOKENS is set, use it for backwards compatibility
                self.OPENAI_MAX_COMPLETION_TOKENS = int(self.OPENAI_MAX_TOKENS)
                warnings.warn(
                    f"OPENAI_MAX_TOKENS is deprecated and will be removed in a future version. "
                    f"Please use OPENAI_MAX_COMPLETION_TOKENS={self.OPENAI_MAX_COMPLETION_TOKENS} instead.",
                    DeprecationWarning,
                    stacklevel=2
                )
        
        # Create upload directory if it doesn't exist
        upload_path = Path(self.UPLOAD_DIRECTORY)
        upload_path.mkdir(parents=True, exist_ok=True)

settings = Settings()
