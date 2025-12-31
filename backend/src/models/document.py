"""
Document Models for RAG System

This module defines Pydantic models for document-related entities
used in the RAG system.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class DocumentChunk(BaseModel):
    """
    Model representing a chunk of document content.

    This is used for storing document content in the vector database
    with associated metadata for retrieval.
    """
    id: str
    content: str
    document_id: str
    chapter: str
    section_title: str
    position: int
    token_count: Optional[int] = None
    metadata: Dict[str, Any] = {}


class DocumentMetadata(BaseModel):
    """
    Model representing metadata about a full document.
    """
    document_id: str
    title: str
    chapter: str
    section: Optional[str] = None
    page_reference: Optional[str] = None
    url_path: str
    word_count: int
    embedding_status: str = "pending"  # pending, processing, completed, failed
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = {}


class DocumentIngestionRequest(BaseModel):
    """
    Model for document ingestion requests.
    """
    content: str
    document_id: str
    chapter_id: str
    section_title: Optional[str] = None
    metadata: Dict[str, Any] = {}


class DocumentIngestionResponse(BaseModel):
    """
    Model for document ingestion responses.
    """
    status: str
    document_id: str
    chunks_processed: int
    embedding_time_ms: float


class DocumentSearchRequest(BaseModel):
    """
    Model for document search requests.
    """
    query: str
    chapter: Optional[str] = None
    document_id: Optional[str] = None
    limit: int = 10


class DocumentSearchResult(BaseModel):
    """
    Model for individual search results.
    """
    document_id: str
    title: str
    section: str
    url_path: str
    relevance_score: float
    preview: str


class DocumentSearchResponse(BaseModel):
    """
    Model for document search responses.
    """
    results: list[DocumentSearchResult]


class ChatQuery(BaseModel):
    """
    Model representing a chat query from a user.
    """
    question: str
    session_id: Optional[str] = None
    selected_text: Optional[str] = None
    mode: str = "normal"  # 'normal' or 'selected-text'
    page_context: Optional[str] = None
    metadata: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    """
    Model representing a response to a chat query.
    """
    response_id: str
    answer: str
    sources: List[Dict[str, Any]] = []
    confidence_score: float = 0.0
    mode: str = "normal"  # 'normal' or 'selected-text'
    timestamp: str = ""
    grounding_validation: bool = True
    tokens_used: int = 0


class ChatSession(BaseModel):
    """
    Model representing a chat session.
    """
    session_id: str
    user_id: Optional[str] = None
    created_at: str = ""
    last_activity: str = ""
    conversation_history: List[Dict[str, Any]] = []
    page_context: Optional[str] = None
    metadata: Dict[str, Any] = {}