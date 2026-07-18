from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(default="EZApply", description="Application name")
    api_version: str = Field(default="0.5.4", description="API version")
    environment: Literal["development", "production"] = Field(
        default="development", description="Application environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    database_url: str = Field(
        default="sqlite:///./app.db", description="Database connection URL"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
