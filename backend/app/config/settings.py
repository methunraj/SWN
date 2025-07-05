from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application
    app_name: str = Field(default="Swift Neethi Backend")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:3000"])
    
    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_default_model: str = Field(default="llama2")
    
    # Llama.cpp Configuration
    llamacpp_base_url: str = Field(default="http://localhost:1234")
    llamacpp_model_path: str = Field(default="./models/")
    llamacpp_default_model: str = Field(default="mistral-7b-instruct")
    
    # Agent Configuration
    max_context_length: int = Field(default=4096)
    default_temperature: float = Field(default=0.7)
    default_top_p: float = Field(default=0.9)
    default_top_k: int = Field(default=40)
    
    # Default Model Configuration
    default_provider: str = Field(default="llamacpp")
    default_model: str = Field(default="qwen/qwen3-4b")
    default_max_tokens: int = Field(default=2048)
    
    # Security
    secret_key: str = Field(default="your-secret-key-here")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # Database
    database_url: Optional[str] = Field(default="sqlite:///./swift_neethi.db")
    
    # Redis
    redis_url: Optional[str] = Field(default=None)
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()