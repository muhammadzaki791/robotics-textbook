"""
Database Utilities for Neon Postgres

This module provides utility functions for database operations,
including session management, transaction handling, and health checks.
"""
from typing import Generator, Optional, Callable, Any
from contextlib import contextmanager
import logging
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps

from src.database.connection import get_db, db_manager


logger = logging.getLogger(__name__)


def with_db_session(func: Callable) -> Callable:
    """
    Decorator to automatically handle database sessions for a function.

    The function should expect a 'db' parameter as its first argument.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with db_manager.get_db_session() as db:
            # Insert the db session as the first argument if it's not already provided
            if 'db' not in kwargs and (len(args) == 0 or not isinstance(args[0], Session)):
                args = (db,) + args
            elif 'db' in kwargs:
                kwargs['db'] = db

            return func(*args, **kwargs)
    return wrapper


@contextmanager
def transactional_session() -> Generator[Session, None, None]:
    """
    Context manager that ensures a transaction is committed or rolled back appropriately.

    Yields:
        Database session
    """
    with db_manager.get_db_session() as session:
        try:
            yield session
            # Commit is handled by the db_manager context manager
        except Exception as e:
            logger.error(f"Transaction failed, rolling back: {e}")
            # Rollback is handled by the db_manager context manager
            raise


def execute_in_transaction(func: Callable) -> Callable:
    """
    Decorator to run a function within a database transaction.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with transactional_session() as db:
            # Inject the session into the function if it expects it
            func_args = args
            if args and isinstance(args[0], Session):
                # Session is already provided as first argument
                pass
            elif 'db' in kwargs:
                kwargs['db'] = db
            else:
                # Insert session as first argument
                func_args = (db,) + args

            return func(*func_args, **kwargs)
    return wrapper


class DatabaseHealthChecker:
    """
    Class to perform various database health checks.
    """

    @staticmethod
    def check_connection(db: Session) -> bool:
        """
        Check if database connection is working.

        Args:
            db: Database session

        Returns:
            True if connection is working, False otherwise
        """
        try:
            result = db.execute("SELECT 1").fetchone()
            return result is not None
        except SQLAlchemyError as e:
            logger.error(f"Connection check failed: {e}")
            return False

    @staticmethod
    def check_table_access(db: Session, table_name: str) -> bool:
        """
        Check if a specific table can be accessed.

        Args:
            db: Database session
            table_name: Name of the table to check

        Returns:
            True if table is accessible, False otherwise
        """
        try:
            result = db.execute(f"SELECT COUNT(*) FROM {table_name} LIMIT 1").fetchone()
            return result is not None
        except SQLAlchemyError as e:
            logger.error(f"Table access check for {table_name} failed: {e}")
            return False

    @staticmethod
    def check_basic_performance(db: Session) -> dict:
        """
        Perform a basic performance check.

        Args:
            db: Database session

        Returns:
            Dictionary with performance metrics
        """
        import time

        start_time = time.time()

        try:
            # Simple query performance test
            db.execute("SELECT 1").fetchone()
            query_time = time.time() - start_time

            # More complex query to test performance
            start_time = time.time()
            db.execute("SELECT COUNT(*) FROM information_schema.tables").fetchone()
            complex_query_time = time.time() - start_time

            return {
                "simple_query_time_ms": round(query_time * 1000, 2),
                "complex_query_time_ms": round(complex_query_time * 1000, 2),
                "status": "healthy"
            }
        except SQLAlchemyError as e:
            logger.error(f"Performance check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


class SessionManager:
    """
    Advanced session management utilities.
    """

    @staticmethod
    def get_session_with_timeout(timeout: int = 30) -> Generator[Session, None, None]:
        """
        Get a database session with a specific timeout.

        Args:
            timeout: Timeout in seconds

        Yields:
            Database session
        """
        # Note: In SQLAlchemy, statement timeout is typically set at the connection level
        # For Neon, we can set this via the connect_args when creating the engine
        with db_manager.get_db_session() as session:
            # Set statement timeout for this session (PostgreSQL specific)
            session.execute(f"SET statement_timeout = {timeout * 1000}")
            yield session

    @staticmethod
    def batch_operation(db: Session, operation_func: Callable, items: list, batch_size: int = 100):
        """
        Execute a database operation in batches to manage memory and performance.

        Args:
            db: Database session
            operation_func: Function to execute on each item
            items: List of items to process
            batch_size: Size of each batch
        """
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            for item in batch:
                operation_func(db, item)

            # Commit each batch to manage memory usage
            db.commit()
            logger.debug(f"Completed batch {i//batch_size + 1}/{(len(items)-1)//batch_size + 1}")


# Convenience functions for common operations
def get_session_context() -> Generator[Session, None, None]:
    """
    Get a database session context with proper cleanup.

    Yields:
        Database session
    """
    return db_manager.get_db_session()


def run_db_health_check() -> dict:
    """
    Run a comprehensive database health check.

    Returns:
        Dictionary with health check results
    """
    health_data = {
        "checks": {},
        "overall_status": "healthy"
    }

    # Test connection
    with get_session_context() as db:
        checker = DatabaseHealthChecker()

        # Connection check
        conn_ok = checker.check_connection(db)
        health_data["checks"]["connection"] = {
            "status": "healthy" if conn_ok else "unhealthy",
            "ok": conn_ok
        }

        if not conn_ok:
            health_data["overall_status"] = "unhealthy"
            return health_data

        # Table access checks for our main tables
        tables_to_check = ["document_metadata", "chat_queries", "chat_responses", "user_sessions"]
        for table in tables_to_check:
            table_ok = checker.check_table_access(db, table)
            health_data["checks"][f"table_{table}"] = {
                "status": "healthy" if table_ok else "unhealthy",
                "ok": table_ok
            }

            if not table_ok:
                health_data["overall_status"] = "unhealthy"

        # Performance check
        perf_data = checker.check_basic_performance(db)
        health_data["checks"]["performance"] = perf_data

        if perf_data["status"] == "unhealthy":
            health_data["overall_status"] = "unhealthy"

    # Pool status
    try:
        pool_status = db_manager.get_pool_status()
        health_data["checks"]["pool"] = {
            "status": "healthy",
            "pool_status": pool_status
        }
    except Exception as e:
        logger.error(f"Pool status check failed: {e}")
        health_data["checks"]["pool"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["overall_status"] = "unhealthy"

    return health_data


# Async session utilities
async def get_async_db() -> Generator[Session, None, None]:
    """
    Async version of get_db for use with async endpoints.

    Yields:
        Database session
    """
    loop = asyncio.get_event_loop()
    with db_manager.get_db_session() as session:
        # In a real async implementation, you might need to handle this differently
        # depending on your async database library (asyncpg, databases, etc.)
        yield session


def close_all_connections():
    """
    Close all database connections.
    """
    db_manager.dispose_engine()
    logger.info("All database connections closed")


# Example usage and testing function
def main():
    """
    Main function to demonstrate database utilities.
    """
    print("Testing database utilities...")

    # Test health check
    health = run_db_health_check()
    print(f"Database health: {health['overall_status']}")
    print(f"Health details: {health['checks']}")

    # Test transactional session
    @execute_in_transaction
    def test_transaction(db: Session):
        # This function runs within a transaction
        result = db.execute("SELECT version()").fetchone()
        print(f"PostgreSQL version: {result[0]}")
        return True

    success = test_transaction()
    print(f"Transaction test: {'Passed' if success else 'Failed'}")

    # Test batch operation (example)
    with get_session_context() as db:
        print("Session context manager working properly")


if __name__ == "__main__":
    main()