"""Configuration module for Certificate Manager."""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application credentials
    APP_URL: str
    APP_USERNAME: str
    APP_PASSWORD: str
    
    # Browser settings
    HEADLESS: bool = False
    WINDOW_SIZE: str = "1920,1080"
    CHROME_BINARY: Optional[str] = None
    BLOCK_IMAGES: int = 2
    
    # Timeouts
    DEFAULT_TIMEOUT: int = 10
    LONG_TIMEOUT: int = 30
    
    # Data files
    DATA_FILE: str = "data/certificates.csv"
    
    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    SCREENSHOTS_DIR: Path = BASE_DIR / "screenshots"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
