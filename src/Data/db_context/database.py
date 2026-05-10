"""Database connection and session configuration"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator

from src.infrastructure.configuration.settings import settings

# Create engine with MySQL configuration
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
    echo=settings.DATABASE_ECHO,
    connect_args={
        "connect_timeout": 10,
        "charset": "utf8mb4",
        "collation": "utf8mb4_0900_as_cs",
        "use_unicode": True,
    }
)

# MySQL-specific session settings
@event.listens_for(engine, "connect")
def set_mysql_session_vars(dbapi_connection, connection_record):
    """Set MySQL session variables on connection"""
    cursor = dbapi_connection.cursor()
    cursor.execute("SET time_zone = '-03:00'")
    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.execute("SET NAMES utf8mb4")
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")
    cursor.execute("SET collation_connection = utf8mb4_0900_as_cs")
    cursor.close()

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    Use this for FastAPI dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session() -> Session:
    """
    Get a database session for non-FastAPI contexts (console apps, scripts).
    Remember to close it manually!
    """
    return SessionLocal()