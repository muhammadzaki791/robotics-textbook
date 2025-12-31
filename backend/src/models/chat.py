from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID, uuid4


class SourceReference(BaseModel):
    """
    Model representing a source reference for a chat response.
    """
    source: str
    section: str = ""
    page: Optional[int] = None


class ChatQuery(BaseModel):
    """
    Model representing a chat query from the user.
    """
    question: str
    query_id: str = str(uuid4())
    selected_text: Optional[str] = None  # For US2 (selected-text mode)
    conversation_history: Optional[List[dict]] = None  # For US3 (contextual learning support)
    session_id: Optional[str] = None  # For tracking conversation sessions


class ChatResponse(BaseModel):
    """
    Model representing a chat response from the system.
    """
    answer: str
    sources: List[SourceReference]
    query_id: str
    context_references: Optional[List[dict]] = None  # For US3 (contextual learning support)