import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URL

if not DATABASE_URL or not DATABASE_URL.startswith("postgresql"):
    raise ValueError("Strict PostgreSQL configuration required: DATABASE_URL must start with 'postgresql://'")

# Initialize SQLAlchemy Engine for PostgreSQL exclusively
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency function providing a PostgreSQL database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
