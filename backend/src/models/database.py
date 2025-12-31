"""
Database Models for RAG System

This module defines SQLAlchemy models for the PostgreSQL database
used in the RAG system.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON, BigInteger, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ARRAY
from sqlalchemy.sql import func
import uuid
from typing import Optional
from datetime import datetime

from src.config.settings import settings


# Create base class for models
Base = declarative_base()


class DocumentMetadataDB(Base):
    """
    Database model for document metadata.

    Stores metadata about textbook documents, chapters, and sections for proper mapping and organization.
    """
    __tablename__ = "document_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    chapter = Column(String(255), nullable=False, index=True)
    section = Column(String(255), nullable=True)
    page_reference = Column(String(100), nullable=True)
    url_path = Column(String(500), nullable=False)
    word_count = Column(Integer, nullable=False)
    embedding_status = Column(String(20), default='pending', nullable=False)  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    checksum = Column(String(64), nullable=True)  # For content change detection
    metadata_json = Column(JSON, nullable=True)  # Additional metadata as JSON

    # Index for faster queries
    __table_args__ = (
        Index('idx_document_metadata_chapter', 'chapter'),
        Index('idx_document_metadata_embedding_status', 'embedding_status'),
    )


class ChatQuery(Base):
    """
    Database model for chat queries.

    Represents a user's question and associated context, including the question text,
    selected text (if any), and user session information.
    """
    __tablename__ = "chat_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    question = Column(Text, nullable=False)
    selected_text = Column(Text, nullable=True)
    mode = Column(String(20), default='normal', nullable=False)  # 'normal' or 'selected-text'
    retrieved_context = Column(JSON, nullable=True)  # Retrieved document chunks as JSON
    embedding = Column(JSON, nullable=True)  # Embedding vector of the question as JSON array
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source_page = Column(String(500), nullable=True)  # Page where query originated (for context)

    # Index for faster queries
    __table_args__ = (
        Index('idx_chat_queries_session_id', 'session_id'),
        Index('idx_chat_queries_timestamp', 'timestamp'),
    )


class ChatResponse(Base):
    """
    Database model for chat responses.

    Represents the system's response to a user query, including the answer text,
    source references, and confidence level.
    """
    __tablename__ = "chat_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # References chat_queries.id
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # Source document references as JSON
    confidence_score = Column(Float(2), nullable=True)  # Confidence in the response (0.0-1.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    grounding_validation = Column(Integer, default=1, nullable=False)  # Whether response is properly grounded (0=False, 1=True)
    tokens_used = Column(Integer, nullable=True)  # Number of tokens in the response

    # Index for faster queries
    __table_args__ = (
        Index('idx_chat_responses_query_id', 'query_id'),
        Index('idx_chat_responses_timestamp', 'timestamp'),
    )


class UserSession(Base):
    """
    Database model for user sessions.

    Represents a user's interaction session with the chatbot, tracking conversation history
    while respecting privacy requirements.
    """
    __tablename__ = "user_sessions"

    id = Column(String(255), primary_key=True)  # Session identifier
    user_id = Column(String(255), nullable=True, index=True)  # Anonymous user identifier (if available)
    start_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    conversation_history = Column(JSON, nullable=True)  # Limited conversation history as JSON
    page_context = Column(String(500), nullable=True)  # Current page context
    metadata_json = Column(JSON, nullable=True)  # Additional session metadata

    # Index for faster queries
    __table_args__ = (
        Index('idx_user_sessions_last_activity', 'last_activity'),
        Index('idx_user_sessions_user_id', 'user_id'),
    )


# Create engine and session factory
engine = create_engine(settings.DATABASE_URL, pool_size=settings.DATABASE_POOL_SIZE, max_overflow=settings.DATABASE_POOL_OVERFLOW)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function to get database session.

    Used with FastAPI dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.

    This should be called during application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables.

    Use with caution - this will delete all data.
    """
    Base.metadata.drop_all(bind=engine)