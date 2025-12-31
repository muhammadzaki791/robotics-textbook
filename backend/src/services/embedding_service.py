"""
Embedding Service for RAG System using Cohere

This module handles the generation of embeddings using the Cohere API.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
import cohere
from src.config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service class for handling text embeddings using Cohere."""

    def __init__(self):
        """Initialize the embedding service with Cohere client."""
        self.client = cohere.AsyncClient(settings.COHERE_API_KEY)
        self.model = settings.EMBEDDING_MODEL
        self.batch_size = settings.EMBEDDING_BATCH_SIZE

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using Cohere.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = await self.client.embed(
                texts=[text],
                model=self.model,
                input_type="search_document"
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Error generating embedding for text '{text[:50]}...': {e}")
            raise

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using Cohere.
        This replaces the old generate_embeddings method with Cohere implementation.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        try:
            # Process in batches to respect API limits
            all_embeddings = []
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]

                # Replace empty strings with a space to avoid API errors
                processed_batch = []
                for text in batch:
                    if not text or not text.strip():
                        processed_batch.append(" ")
                    else:
                        processed_batch.append(text)

                response = await self.client.embed(
                    texts=processed_batch,
                    model=self.model,
                    input_type="search_document"
                )
                all_embeddings.extend(response.embeddings)

            return all_embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings batch: {e}")
            raise

    async def embed_question(self, question: str, selected_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate embedding for a question, potentially incorporating selected text.

        Args:
            question: The question to embed
            selected_text: Optional selected text to incorporate into the embedding

        Returns:
            Dictionary containing the embedding and metadata
        """
        # For question embedding, we can use a different input_type
        text_to_embed = question
        if selected_text:
            text_to_embed = f"Question: {question} Selected text: {selected_text}"

        try:
            response = await self.client.embed(
                texts=[text_to_embed],
                model=self.model,
                input_type="search_query"  # Use search_query for questions
            )
            return {
                "embedding": response.embeddings[0],
                "text": text_to_embed,
                "model": self.model
            }
        except Exception as e:
            logger.error(f"Error generating question embedding: {e}")
            raise

    async def embed_document_chunks(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks and return with metadata.
        This replaces the old embed_document_chunks method with Cohere implementation.

        Args:
            chunks: List of document chunk texts

        Returns:
            List of dictionaries containing chunk text, embedding, and metadata
        """
        start_time = asyncio.get_event_loop().time()

        # Generate embeddings for all chunks
        embeddings = await self.generate_embeddings(chunks)

        # Create results with metadata
        results = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            results.append({
                'chunk_id': f'chunk_{i}',
                'content': chunk,
                'embedding': embedding,
                'model': self.model
            })

        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000  # Convert to milliseconds
        logger.info(f"Embedded {len(chunks)} chunks in {processing_time:.2f}ms")

        return results

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query using Cohere.
        This replaces the old embed_query method with Cohere implementation.

        Args:
            query: Query text to embed

        Returns:
            Embedding vector
        """
        start_time = asyncio.get_event_loop().time()

        embedding = await self.generate_embedding(query)

        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000  # Convert to milliseconds

        logger.debug(f"Embedded query in {processing_time:.2f}ms")

        return embedding

    async def embed_questions_batch(self, questions: List[str]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a batch of questions using Cohere.
        This replaces the old embed_questions_batch method with Cohere implementation.

        Args:
            questions: List of question strings

        Returns:
            List of dictionaries containing embeddings and metadata
        """
        start_time = asyncio.get_event_loop().time()

        # Generate embeddings for all questions
        embeddings = await self.generate_embeddings(questions)

        total_processing_time = (asyncio.get_event_loop().time() - start_time) * 1000  # Convert to milliseconds

        results = []
        for i, (question, embedding) in enumerate(zip(questions, embeddings)):
            results.append({
                "question_index": i,
                "original_question": question,
                "embedding": embedding,
                "model": self.model
            })

        logger.debug(f"Embedded {len(questions)} questions in {total_processing_time:.2f}ms")

        return results

# Singleton instance
embedding_service = EmbeddingService()