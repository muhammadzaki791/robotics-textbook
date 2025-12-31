"""
PostgreSQL Service for RAG System

This module handles all interactions with the Neon Postgres database,
including CRUD operations for document metadata, chat queries, and user sessions.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import logging

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from sqlalchemy.exc import SQLAlchemyError

from src.models.database import (
    DocumentMetadataDB, ChatQuery, ChatResponse, UserSession, get_db
)
from src.models.document import DocumentMetadata, DocumentChunk


logger = logging.getLogger(__name__)


class PostgresService:
    """Service class for interacting with PostgreSQL database."""

    def __init__(self):
        """Initialize the PostgreSQL service."""
        pass

    def create_document_metadata(self, db: Session, document_metadata: DocumentMetadata) -> DocumentMetadataDB:
        """
        Create a new document metadata record.

        Args:
            db: Database session
            document_metadata: DocumentMetadata object with the data

        Returns:
            Created DocumentMetadataDB object
        """
        try:
            db_doc_metadata = DocumentMetadataDB(
                document_id=document_metadata.document_id,
                title=document_metadata.title,
                chapter=document_metadata.chapter,
                section=document_metadata.section,
                page_reference=document_metadata.page_reference,
                url_path=document_metadata.url_path,
                word_count=document_metadata.word_count,
                embedding_status=document_metadata.embedding_status,
                checksum=document_metadata.checksum,
                metadata_json=document_metadata.metadata_json
            )
            db.add(db_doc_metadata)
            db.commit()
            db.refresh(db_doc_metadata)
            return db_doc_metadata
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating document metadata: {e}")
            raise

    def get_document_metadata(self, db: Session, document_id: str) -> Optional[DocumentMetadataDB]:
        """
        Get document metadata by document ID.

        Args:
            db: Database session
            document_id: ID of the document

        Returns:
            DocumentMetadataDB object if found, None otherwise
        """
        try:
            return db.query(DocumentMetadataDB).filter(
                DocumentMetadataDB.document_id == document_id
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting document metadata: {e}")
            return None

    def update_document_metadata(self, db: Session, document_id: str,
                                updates: Dict[str, Any]) -> Optional[DocumentMetadataDB]:
        """
        Update document metadata.

        Args:
            db: Database session
            document_id: ID of the document to update
            updates: Dictionary of fields to update

        Returns:
            Updated DocumentMetadataDB object if successful, None otherwise
        """
        try:
            db_doc_metadata = db.query(DocumentMetadataDB).filter(
                DocumentMetadataDB.document_id == document_id
            ).first()

            if db_doc_metadata:
                for key, value in updates.items():
                    setattr(db_doc_metadata, key, value)
                db.commit()
                db.refresh(db_doc_metadata)
                return db_doc_metadata

            return None
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating document metadata: {e}")
            return None

    def get_documents_by_chapter(self, db: Session, chapter: str) -> List[DocumentMetadataDB]:
        """
        Get all documents in a specific chapter.

        Args:
            db: Database session
            chapter: Chapter name

        Returns:
            List of DocumentMetadataDB objects
        """
        try:
            return db.query(DocumentMetadataDB).filter(
                DocumentMetadataDB.chapter == chapter
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting documents by chapter: {e}")
            return []

    def get_all_documents(self, db: Session, skip: int = 0, limit: int = 100) -> List[DocumentMetadataDB]:
        """
        Get all documents with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of DocumentMetadataDB objects
        """
        try:
            return db.query(DocumentMetadataDB).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all documents: {e}")
            return []

    def create_chat_query(self, db: Session, session_id: str, question: str,
                         selected_text: Optional[str] = None, mode: str = 'normal',
                         source_page: Optional[str] = None) -> ChatQuery:
        """
        Create a new chat query record.

        Args:
            db: Database session
            session_id: Session identifier
            question: The user's question
            selected_text: Text highlighted by user (if any)
            mode: Chat mode ('normal' or 'selected-text')
            source_page: Page where query originated

        Returns:
            Created ChatQuery object
        """
        try:
            chat_query = ChatQuery(
                session_id=session_id,
                question=question,
                selected_text=selected_text,
                mode=mode,
                source_page=source_page
            )
            db.add(chat_query)
            db.commit()
            db.refresh(chat_query)
            return chat_query
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating chat query: {e}")
            raise

    def get_chat_query(self, db: Session, query_id: UUID) -> Optional[ChatQuery]:
        """
        Get a chat query by ID.

        Args:
            db: Database session
            query_id: ID of the query

        Returns:
            ChatQuery object if found, None otherwise
        """
        try:
            return db.query(ChatQuery).filter(ChatQuery.id == query_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting chat query: {e}")
            return None

    def create_chat_response(self, db: Session, query_id: UUID, content: str,
                           sources: Optional[List[Dict[str, Any]]] = None,
                           confidence_score: Optional[float] = None,
                           grounding_validation: bool = True,
                           tokens_used: Optional[int] = None) -> ChatResponse:
        """
        Create a new chat response record.

        Args:
            db: Database session
            query_id: ID of the corresponding query
            content: The response content
            sources: List of source document references
            confidence_score: Confidence in the response
            grounding_validation: Whether response is properly grounded
            tokens_used: Number of tokens in the response

        Returns:
            Created ChatResponse object
        """
        try:
            chat_response = ChatResponse(
                query_id=query_id,
                content=content,
                sources=sources or [],
                confidence_score=confidence_score,
                grounding_validation=1 if grounding_validation else 0,
                tokens_used=tokens_used
            )
            db.add(chat_response)
            db.commit()
            db.refresh(chat_response)
            return chat_response
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating chat response: {e}")
            raise

    def get_chat_response(self, db: Session, response_id: UUID) -> Optional[ChatResponse]:
        """
        Get a chat response by ID.

        Args:
            db: Database session
            response_id: ID of the response

        Returns:
            ChatResponse object if found, None otherwise
        """
        try:
            return db.query(ChatResponse).filter(ChatResponse.id == response_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting chat response: {e}")
            return None

    def get_chat_history(self, db: Session, session_id: str,
                        limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get chat history for a session.

        Args:
            db: Database session
            session_id: Session identifier
            limit: Maximum number of conversations to return

        Returns:
            List of dictionaries containing query-response pairs
        """
        try:
            # Join queries and responses to get conversation history
            history = db.query(ChatQuery, ChatResponse).join(
                ChatResponse, ChatQuery.id == ChatResponse.query_id
            ).filter(
                ChatQuery.session_id == session_id
            ).order_by(ChatQuery.timestamp.desc()).limit(limit).all()

            result = []
            for query, response in history:
                result.append({
                    'query_id': query.id,
                    'question': query.question,
                    'response_id': response.id,
                    'answer': response.content,
                    'timestamp': query.timestamp,
                    'confidence_score': response.confidence_score
                })

            return result
        except SQLAlchemyError as e:
            logger.error(f"Error getting chat history: {e}")
            return []

    def create_user_session(self, db: Session, session_id: str,
                           user_id: Optional[str] = None,
                           page_context: Optional[str] = None) -> UserSession:
        """
        Create a new user session.

        Args:
            db: Database session
            session_id: Session identifier
            user_id: User identifier (optional)
            page_context: Current page context (optional)

        Returns:
            Created UserSession object
        """
        try:
            user_session = UserSession(
                id=session_id,
                user_id=user_id,
                page_context=page_context
            )
            db.add(user_session)
            db.commit()
            db.refresh(user_session)
            return user_session
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating user session: {e}")
            raise

    def get_user_session(self, db: Session, session_id: str) -> Optional[UserSession]:
        """
        Get a user session by ID.

        Args:
            db: Database session
            session_id: Session identifier

        Returns:
            UserSession object if found, None otherwise
        """
        try:
            return db.query(UserSession).filter(UserSession.id == session_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user session: {e}")
            return None

    def update_user_session(self, db: Session, session_id: str,
                           updates: Dict[str, Any]) -> Optional[UserSession]:
        """
        Update a user session.

        Args:
            db: Database session
            session_id: Session identifier
            updates: Dictionary of fields to update

        Returns:
            Updated UserSession object if successful, None otherwise
        """
        try:
            user_session = db.query(UserSession).filter(UserSession.id == session_id).first()

            if user_session:
                for key, value in updates.items():
                    setattr(user_session, key, value)
                db.commit()
                db.refresh(user_session)
                return user_session

            return None
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating user session: {e}")
            return None

    def get_recent_sessions(self, db: Session, minutes: int = 30) -> List[UserSession]:
        """
        Get user sessions active within the specified time window.

        Args:
            db: Database session
            minutes: Number of minutes to look back

        Returns:
            List of UserSession objects
        """
        try:
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)

            return db.query(UserSession).filter(
                UserSession.last_activity >= cutoff_time
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent sessions: {e}")
            return []

    def get_document_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get statistics about documents in the database.

        Args:
            db: Database session

        Returns:
            Dictionary with document statistics
        """
        try:
            total_documents = db.query(DocumentMetadataDB).count()
            completed_embeddings = db.query(DocumentMetadataDB).filter(
                DocumentMetadataDB.embedding_status == 'completed'
            ).count()
            pending_embeddings = db.query(DocumentMetadataDB).filter(
                DocumentMetadataDB.embedding_status == 'pending'
            ).count()

            # Get word count statistics
            word_count_stats = db.query(
                func.avg(DocumentMetadataDB.word_count).label('avg_words'),
                func.sum(DocumentMetadataDB.word_count).label('total_words'),
                func.max(DocumentMetadataDB.word_count).label('max_words'),
                func.min(DocumentMetadataDB.word_count).label('min_words')
            ).first()

            # Get unique chapters
            unique_chapters = db.query(DocumentMetadataDB.chapter).distinct().count()

            return {
                'total_documents': total_documents,
                'completed_embeddings': completed_embeddings,
                'pending_embeddings': pending_embeddings,
                'avg_words_per_document': float(word_count_stats.avg_words) if word_count_stats.avg_words else 0,
                'total_words': word_count_stats.total_words or 0,
                'max_words_per_document': word_count_stats.max_words or 0,
                'min_words_per_document': word_count_stats.min_words or 0,
                'unique_chapters': unique_chapters
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting document statistics: {e}")
            return {}

    def update_document_checksum(self, db: Session, document_id: str, checksum: str) -> Optional[DocumentMetadataDB]:
        """
        Update the checksum for a document.

        Args:
            db: Database session
            document_id: ID of the document
            checksum: New checksum value

        Returns:
            Updated DocumentMetadataDB object if successful, None otherwise
        """
        try:
            return self.update_document_metadata(db, document_id, {"checksum": checksum})
        except SQLAlchemyError as e:
            logger.error(f"Error updating document checksum: {e}")
            return None

    def get_documents_by_status(self, db: Session, status: str) -> List[DocumentMetadataDB]:
        """
        Get documents by embedding status.

        Args:
            db: Database session
            status: Embedding status to filter by

        Returns:
            List of DocumentMetadataDB objects with the specified status
        """
        try:
            return db.query(DocumentMetadataDB).filter(
                DocumentMetadataDB.embedding_status == status
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting documents by status: {e}")
            return []

    def get_documents_by_url_path(self, db: Session, url_path: str) -> List[DocumentMetadataDB]:
        """
        Get documents by URL path.

        Args:
            db: Database session
            url_path: URL path to filter by

        Returns:
            List of DocumentMetadataDB objects with the specified URL path
        """
        try:
            return db.query(DocumentMetadataDB).filter(
                DocumentMetadataDB.url_path == url_path
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting documents by URL path: {e}")
            return []

    def get_documents_modified_since(self, db: Session, since_datetime: datetime) -> List[DocumentMetadataDB]:
        """
        Get documents modified since a specific datetime.

        Args:
            db: Database session
            since_datetime: Datetime to filter by

        Returns:
            List of DocumentMetadataDB objects modified since the specified datetime
        """
        try:
            return db.query(DocumentMetadataDB).filter(
                DocumentMetadataDB.updated_at >= since_datetime
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting documents modified since: {e}")
            return []

    def get_documents_by_chapter_range(self, db: Session, chapters: List[str]) -> List[DocumentMetadataDB]:
        """
        Get documents from multiple chapters.

        Args:
            db: Database session
            chapters: List of chapter names to filter by

        Returns:
            List of DocumentMetadataDB objects from the specified chapters
        """
        try:
            return db.query(DocumentMetadataDB).filter(
                DocumentMetadataDB.chapter.in_(chapters)
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting documents by chapter range: {e}")
            return []

    def get_document_by_title(self, db: Session, title: str) -> Optional[DocumentMetadataDB]:
        """
        Get a document by its title.

        Args:
            db: Database session
            title: Title of the document

        Returns:
            DocumentMetadataDB object if found, None otherwise
        """
        try:
            return db.query(DocumentMetadataDB).filter(
                DocumentMetadataDB.title == title
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting document by title: {e}")
            return None

    def get_documents_by_word_count_range(self, db: Session, min_words: int, max_words: int) -> List[DocumentMetadataDB]:
        """
        Get documents within a word count range.

        Args:
            db: Database session
            min_words: Minimum word count
            max_words: Maximum word count

        Returns:
            List of DocumentMetadataDB objects within the word count range
        """
        try:
            return db.query(DocumentMetadataDB).filter(
                and_(
                    DocumentMetadataDB.word_count >= min_words,
                    DocumentMetadataDB.word_count <= max_words
                )
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting documents by word count range: {e}")
            return []

    def get_all_chapters(self, db: Session) -> List[str]:
        """
        Get all unique chapter names.

        Args:
            db: Database session

        Returns:
            List of unique chapter names
        """
        try:
            result = db.query(DocumentMetadataDB.chapter).distinct().all()
            return [row[0] for row in result]
        except SQLAlchemyError as e:
            logger.error(f"Error getting all chapters: {e}")
            return []

    def get_documents_with_metadata_field(self, db: Session, metadata_key: str) -> List[DocumentMetadataDB]:
        """
        Get documents that have a specific metadata field.

        Args:
            db: Database session
            metadata_key: Key name to check for in metadata

        Returns:
            List of DocumentMetadataDB objects that have the specified metadata key
        """
        try:
            # Use JSON operators to check if the metadata contains the key
            return db.query(DocumentMetadataDB).filter(
                func.jsonb_exists(DocumentMetadataDB.metadata_json, metadata_key)
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting documents with metadata field: {e}")
            return []

    def update_multiple_documents(self, db: Session, document_ids: List[str],
                                 updates: Dict[str, Any]) -> int:
        """
        Update multiple documents at once.

        Args:
            db: Database session
            document_ids: List of document IDs to update
            updates: Dictionary of fields to update

        Returns:
            Number of documents updated
        """
        try:
            updated_count = db.query(DocumentMetadataDB).filter(
                DocumentMetadataDB.document_id.in_(document_ids)
            ).update(updates, synchronize_session=False)

            db.commit()
            return updated_count
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating multiple documents: {e}")
            return 0

    def get_chat_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get statistics about chat interactions.

        Args:
            db: Database session

        Returns:
            Dictionary with chat statistics
        """
        try:
            total_queries = db.query(ChatQuery).count()
            total_responses = db.query(ChatResponse).count()

            # Get queries per hour
            from datetime import datetime, timedelta
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            queries_last_hour = db.query(ChatQuery).filter(
                ChatQuery.timestamp >= one_hour_ago
            ).count()

            # Get average response confidence
            avg_confidence = db.query(func.avg(ChatResponse.confidence_score)).scalar()

            # Get active sessions (sessions with activity in last 30 minutes)
            active_sessions = self.get_recent_sessions(db, minutes=30)

            return {
                'total_queries': total_queries,
                'total_responses': total_responses,
                'queries_last_hour': queries_last_hour,
                'avg_response_confidence': float(avg_confidence) if avg_confidence else 0.0,
                'active_sessions': len(active_sessions)
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting chat statistics: {e}")
            return {}


# Singleton instance
postgres_service = PostgresService()