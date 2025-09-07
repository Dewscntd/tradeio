from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from app.core.config import settings

# SQLAlchemy engine and session factory
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Yield a SQLAlchemy session and ensure it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()