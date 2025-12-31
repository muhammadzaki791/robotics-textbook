"""
Database Connection and Session Management for Neon Postgres

This module handles connection pooling, session management, and database
operations for the Neon Postgres database used in the RAG system.
"""
from typing import Generator, Optional
from contextlib import contextmanager
import logging
import time
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
import psycopg
from urllib.parse import urlparse

from src.config.settings import settings


logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """
    Manages database connections and sessions for the Neon Postgres database.
    """

    def __init__(self):
        """Initialize the database connection manager."""
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize the database engine with proper configuration for Neon."""
        try:
            # Parse the database URL to extract connection parameters
            parsed_url = urlparse(settings.DATABASE_URL)

            # Configure engine with Neon-specific settings
            self.engine = create_engine(
                settings.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_POOL_OVERFLOW,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=300,    # Recycle connections every 5 minutes
                echo=False,          # Set to True for SQL logging
                connect_args={
                    "application_name": "rag-chatbot-backend",
                    "options": "-c statement_timeout=30000",  # 30 second timeout
                }
            )

            # Add event listeners for connection monitoring
            event.listen(self.engine, 'connect', self._set_sqlite_pragma)

            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            logger.info("Database engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise

    def _set_sqlite_pragma(self, dbapi_connection, connection_record):
        """Set connection-specific settings (for PostgreSQL/Neon)."""
        # This is a placeholder - for PostgreSQL/Neon we don't need SQLite pragmas
        # But we can set other connection-specific settings here if needed
        pass

    def get_session(self) -> Session:
        """
        Get a database session.

        Returns:
            Database session
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database engine not initialized")

        return self.SessionLocal()

    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.

        Yields:
            Database session
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def test_connection(self) -> bool:
        """
        Test the database connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.get_db_session() as session:
                # Execute a simple query to test the connection
                result = session.execute("SELECT 1")
                return result.fetchone()[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def get_pool_status(self) -> dict:
        """
        Get information about the connection pool.

        Returns:
            Dictionary with pool status information
        """
        if self.engine is None:
            return {"error": "Engine not initialized"}

        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in_connections": pool.checkedin(),
            "checked_out_connections": pool.checkedout(),
            "overflow_connections": pool.overflow(),
            "pool_hits": getattr(pool, 'hits', 0),
            "pool_timeouts": getattr(pool, 'timeouts', 0)
        }

    def dispose_engine(self):
        """Dispose of the database engine."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine disposed")


# Global instance of the connection manager
db_manager = DatabaseConnectionManager()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get database session.

    Yields:
        Database session
    """
    with db_manager.get_db_session() as session:
        yield session


def init_db():
    """Initialize the database by creating all tables."""
    from src.models.database import Base
    try:
        Base.metadata.create_all(bind=db_manager.engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def check_db_health() -> dict:
    """
    Check the health of the database connection.

    Returns:
        Dictionary with health check results
    """
    start_time = time.time()

    connection_ok = db_manager.test_connection()
    pool_status = db_manager.get_pool_status()

    response_time = time.time() - start_time

    return {
        "status": "healthy" if connection_ok else "unhealthy",
        "response_time_ms": round(response_time * 1000, 2),
        "connection_ok": connection_ok,
        "pool_status": pool_status
    }


def close_db_connections():
    """Close all database connections."""
    db_manager.dispose_engine()


# Test connection function
def main():
    """Main function to test database connection."""
    print("Testing database connection...")

    # Test the connection
    is_connected = db_manager.test_connection()
    print(f"Database connection: {'Successful' if is_connected else 'Failed'}")

    if is_connected:
        # Print pool status
        pool_status = db_manager.get_pool_status()
        print(f"Pool status: {pool_status}")

        # Test a simple operation
        try:
            with db_manager.get_db_session() as session:
                result = session.execute("SELECT version()").fetchone()
                print(f"PostgreSQL version: {result[0]}")
        except Exception as e:
            print(f"Error executing test query: {e}")
    else:
        print("Could not establish database connection")


if __name__ == "__main__":
    main()