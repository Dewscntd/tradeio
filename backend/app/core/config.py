from pydantic import BaseSettings
from typing import List, Dict, Any
import os

class Settings(BaseSettings):
    # App settings
    PROJECT_NAME: str = "AI Trading Bot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "trader")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "trading_bot")
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Trading settings (Israeli market specific)
    TRADING_ENABLED: bool = False  # Start with paper trading
    MAX_DAILY_LOSS: float = 0.03  # 3%
    MAX_POSITION_SIZE: float = 0.15  # 15%
    TASE_TRADING_HOURS: Dict[str, str] = {"start": "10:00", "end": "17:25"}
    US_TRADING_HOURS: Dict[str, str] = {"start": "16:30", "end": "23:00"}  # Israel time
    
    # Broker settings
    IB_HOST: str = os.getenv("IB_HOST", "127.0.0.1")
    IB_PORT: int = int(os.getenv("IB_PORT", "7497"))  # Paper trading port
    IB_CLIENT_ID: int = int(os.getenv("IB_CLIENT_ID", "1"))
    
    class Config:
        env_file = ".env"

settings = Settings()
