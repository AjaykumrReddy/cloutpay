import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

# Engine configuration (production-grade)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # Avoid stale connections
    pool_size=10,             # Base connections
    max_overflow=20,          # Extra connections
    pool_timeout=30,          # Wait time before timeout
    pool_recycle=1800,        # Recycle connections (important for Supabase)
    echo=False                # Set True only for debugging
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base model
Base = declarative_base()


# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session per request.
    Handles commit/rollback and ensures proper cleanup.
    """
    db: Session = SessionLocal()

    try:
        yield db
        db.commit()  # commit if everything is fine

    except SQLAlchemyError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
