from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import os
import google.generativeai as genai

from ...models.chat import ChatQuery, ChatResponse
from ...services.chat_service import ChatService
from ...services.retrieval_service import RetrievalService
from ...database.connection import get_db
from ...services.qdrant_service import qdrant_service
from ...config.settings import settings

router = APIRouter(tags=["chat"])

# Initialize services (these would typically be dependency injected in a more complex setup)
async def get_chat_service() -> ChatService:
    # Use the global qdrant_service instance via the retrieval service singleton
    from ...services.retrieval_service import retrieval_service

    # Initialize Gemini client
    genai.configure(api_key=settings.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)

    return ChatService(retrieval_service=retrieval_service, gemini_client=gemini_model)


@router.post("/ask", response_model=ChatResponse)
async def ask_question(chat_query: ChatQuery) -> ChatResponse:
    """
    Endpoint to ask questions about the textbook content.

    If no relevant content is found in the textbook, the response will be:
    "The answer is not found in the book."
    """
    try:
        chat_service = await get_chat_service()
        response = await chat_service.process_query(chat_query)

        # In a real implementation, you might want to log the query and response
        # for analytics or debugging purposes

        return response
    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except Exception as e:
        # Log the error appropriately in a real implementation
        print(f"Error processing chat query: {str(e)}")

        # Return a not found response if there's an error
        from uuid import uuid4
        return ChatResponse(
            answer="The answer is not found in the book.",
            sources=[],
            query_id=chat_query.query_id or str(uuid4())
        )


@router.get("/health")
async def chat_health_check():
    """
    Health check endpoint for the chat service.
    """
    return {"status": "healthy", "service": "chat"}