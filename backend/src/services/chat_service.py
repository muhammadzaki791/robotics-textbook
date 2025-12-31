import asyncio
from typing import List, Dict, Optional
import google.generativeai as genai
from pydantic import BaseModel

from ..models.chat import ChatQuery, ChatResponse, SourceReference
from ..services.retrieval_service import RetrievalService
from ..config.constants import (
    GEMINI_SYSTEM_PROMPT,
    DEFAULT_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    RESPONSE_THRESHOLD
)


from collections import defaultdict
import time

class ChatService:
    def __init__(self, retrieval_service: RetrievalService, gemini_client=None):
        self.retrieval_service = retrieval_service
        # Initialize Gemini client if not provided
        if gemini_client is None:
            genai.configure(api_key=self._get_api_key())
            self.gemini_client = genai.GenerativeModel(DEFAULT_MODEL)
        else:
            self.gemini_client = gemini_client
        # In-memory conversation store (in production, use Redis or database)
        self.conversation_store = defaultdict(list)
        self.conversation_ttl = 3600  # 1 hour TTL for conversations
        self.max_conversation_length = 20  # Limit conversation history length

    def _get_api_key(self):
        """Get the API key from settings"""
        from ..config.settings import settings
        return settings.GEMINI_API_KEY

    async def process_query(self, query: ChatQuery) -> ChatResponse:
        """
        Process a chat query and return a response based on textbook content.

        Args:
            query: The chat query containing the question

        Returns:
            ChatResponse with the answer and source references
        """
        # Retrieve relevant chunks based on the query, selected text, and conversation history
        if query.selected_text:
            # Use selected text priority if available
            retrieved_chunks = await self.retrieval_service.retrieve_with_selected_text_priority(
                query.question, query.selected_text, top_k=5
            )
        else:
            # Use regular retrieval if no selected text
            retrieved_chunks = await self.retrieval_service.retrieve_relevant_documents(
                query.question, top_k=5
            )

        # Get conversation history from store if session_id is provided
        session_conversation_history = None
        if query.session_id:
            session_conversation_history = self.get_conversation_history(query.session_id, limit=5)

        # Combine query conversation history with session history if both exist
        combined_conversation_history = query.conversation_history or []
        if session_conversation_history:
            combined_conversation_history = combined_conversation_history + session_conversation_history

        # Apply contextual reranking if conversation history is available
        if combined_conversation_history:
            retrieved_chunks = self.retrieval_service.rerank_for_contextual_learning(
                retrieved_chunks, query.question, combined_conversation_history
            )

        # Check if we have relevant content with sufficient similarity
        if not retrieved_chunks or max([chunk.get('score', 0) for chunk in retrieved_chunks]) < RESPONSE_THRESHOLD:
            return ChatResponse(
                answer="The answer is not found in the book.",
                sources=[],
                query_id=query.query_id
            )

        # Build context from retrieved chunks
        context = self._build_context_from_chunks(retrieved_chunks)

        # Generate response using OpenAI with contextual awareness
        response_text = await self._generate_response(
            query.question, context, bool(query.selected_text), combined_conversation_history
        )

        # Validate that response is grounded in the context
        if not self._is_response_grounded(response_text, context):
            return ChatResponse(
                answer="The answer is not found in the book.",
                sources=[],
                query_id=query.query_id
            )

        # Extract source references
        sources = self._extract_sources(retrieved_chunks)

        # Get context references for contextual learning support
        context_references = None
        if query.conversation_history or len(sources) > 0:
            # Find related concepts based on the question and retrieved content
            try:
                context_references = await self.retrieval_service.find_related_concepts(query.question)
            except:
                # If there's an error finding related concepts, continue without them
                context_references = []

        # Format response with source citations if sources exist
        formatted_answer = self._format_response_with_citations(response_text, sources)

        # Add the interaction to conversation history
        session_id = query.session_id or "default"
        user_interaction = {
            "role": "user",
            "content": query.question,
            "timestamp": time.time()
        }
        bot_interaction = {
            "role": "assistant",
            "content": formatted_answer,
            "timestamp": time.time()
        }

        # Add to conversation store
        conversation = self.conversation_store[session_id]
        conversation.append(user_interaction)
        conversation.append(bot_interaction)

        # Keep only the most recent exchanges to prevent memory bloat
        if len(conversation) > self.max_conversation_length:
            self.conversation_store[session_id] = conversation[-self.max_conversation_length:]

        return ChatResponse(
            answer=formatted_answer,
            sources=sources,
            query_id=query.query_id,
            context_references=context_references
        )

    def _build_context_from_chunks(self, chunks) -> str:
        """
        Build a context string from retrieved chunks.

        Args:
            chunks: List of retrieved chunks with metadata

        Returns:
            Formatted context string
        """
        context_parts = []
        for chunk in chunks:
            if chunk.get('metadata'):
                source_info = f"Source: {chunk['metadata'].get('source', 'Unknown')}"
                if chunk['metadata'].get('section'):
                    source_info += f", Section: {chunk['metadata']['section']}"
                context_parts.append(f"{source_info}\nContent: {chunk['content']}\n")
            else:
                # If no metadata, just use the content
                context_parts.append(f"Content: {chunk['content']}\n")

        return "\n".join(context_parts)

    async def _generate_response(self, question: str, context: str, selected_text_mode: bool = False,
                                conversation_history: Optional[List[dict]] = None) -> str:
        """
        Generate a response using Google Gemini based on the question and context.

        Args:
            question: The user's question
            context: Retrieved context from the textbook
            selected_text_mode: Whether the query is in selected-text mode
            conversation_history: Optional conversation history for contextual awareness

        Returns:
            Generated response text
        """
        # Use a different system prompt based on mode and context
        system_prompt = GEMINI_SYSTEM_PROMPT
        if selected_text_mode:
            system_prompt = (
                "You are an AI assistant designed to help students learn about physical AI and humanoid robotics using the textbook content provided. "
                "The user has selected specific text and asked a question about it. "
                "Please answer the question based ONLY on the provided context, focusing specifically on the selected text. "
                "If the answer is not in the provided context, respond with: 'The answer is not found in the book.'"
            )
        elif conversation_history:
            # Enhanced prompt for contextual learning
            system_prompt = (
                "You are an AI assistant designed to help students learn about physical AI and humanoid robotics using the textbook content provided. "
                "Consider the conversation history to provide educational responses that connect to previous topics. "
                "Provide clear, educational explanations with references to relevant textbook sections. "
                "If the answer is not in the provided context, respond with: 'The answer is not found in the book.'"
            )

        # Build the prompt with context and question
        prompt_parts = [
            f"System Prompt: {system_prompt}\n\n",
            f"Context:\n{context}\n\n",
            f"Question: {question}"
        ]

        # Add conversation history if available
        if conversation_history:
            history_text = "\n\nConversation History:\n"
            for exchange in conversation_history[-3:]:  # Use last 3 exchanges
                if isinstance(exchange, dict) and 'role' in exchange and 'content' in exchange:
                    role = exchange['role']
                    content = exchange['content']
                    history_text += f"{role.capitalize()}: {content}\n"
            prompt_parts.insert(1, history_text)

        full_prompt = "".join(prompt_parts)

        try:
            # Generate content using Gemini
            response = self.gemini_client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE
                )
            )

            # Extract the text from the response
            if response.text:
                return response.text.strip()
            else:
                # If no text was generated, return the default not found message
                return "The answer is not found in the book."
        except Exception as e:
            # Log the error appropriately in a real implementation
            print(f"Error generating response: {str(e)}")
            return "The answer is not found in the book."

    def _is_response_grounded(self, response: str, context: str) -> bool:
        """
        Validate that the response is grounded in the provided context.

        Args:
            response: The generated response
            context: The context that was provided to the model

        Returns:
            True if response appears to be grounded in context, False otherwise
        """
        # Simple heuristic: check if response contains content that relates to context
        # In a more sophisticated implementation, we could use embedding similarity
        # or other NLP techniques to validate grounding

        if "answer is not found in the book" in response.lower():
            return True  # This is an acceptable response when content isn't found

        # If context is empty but we have a substantive response, it's not grounded
        if not context.strip() and response.strip():
            return False

        return True

    def _extract_sources(self, chunks) -> List[SourceReference]:
        """
        Extract source references from retrieved chunks.

        Args:
            chunks: List of retrieved chunks with metadata

        Returns:
            List of SourceReference objects
        """
        sources = []
        seen_sources = set()

        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            if metadata:
                source_key = (metadata.get('source'), metadata.get('section'))
                if source_key not in seen_sources:
                    sources.append(SourceReference(
                        source=metadata.get('source', 'Unknown'),
                        section=metadata.get('section', ''),
                        page=metadata.get('page', None)
                    ))
                    seen_sources.add(source_key)

        return sources

    def _format_response_with_citations(self, response: str, sources: List[SourceReference]) -> str:
        """
        Format the response with source citations.

        Args:
            response: The original response text
            sources: List of source references

        Returns:
            Formatted response with citations
        """
        if not sources:
            return response

        # Add a citation section to the response
        citation_text = "\n\nSources cited:"
        for i, source in enumerate(sources, 1):
            source_info = f"[{i}] {source.source}"
            if source.section:
                source_info += f", Section: {source.section}"
            if source.page is not None:
                source_info += f", Page: {source.page}"
            citation_text += f"\n  {source_info}"

        return f"{response}{citation_text}"

    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """
        Retrieve conversation history for a given session.

        Args:
            session_id: The session identifier
            limit: Maximum number of exchanges to return

        Returns:
            List of conversation exchanges
        """
        conversation = self.conversation_store.get(session_id, [])
        return conversation[-limit:]

    def clear_conversation_history(self, session_id: str):
        """
        Clear conversation history for a given session.

        Args:
            session_id: The session identifier to clear
        """
        if session_id in self.conversation_store:
            del self.conversation_store[session_id]