"""
Retrieval Service for RAG System

This module handles the retrieval of relevant documents based on vector similarity
using the Qdrant vector database. It implements top-k search and context assembly.
"""
import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
import logging
from uuid import uuid4

from src.services.qdrant_service import qdrant_service
from src.services.embedding_service import embedding_service
from src.config.settings import settings


logger = logging.getLogger(__name__)


class RetrievalService:
    """Service class for handling document retrieval based on vector similarity."""

    def __init__(self):
        """Initialize the retrieval service with required dependencies."""
        self.qdrant_service = qdrant_service
        self.embedding_service = embedding_service
        self.top_k = settings.RETRIEVAL_TOP_K
        self.min_score = settings.RETRIEVAL_MIN_SCORE

    async def retrieve_relevant_documents(self, query: str, selected_text: Optional[str] = None,
                                        top_k: Optional[int] = None, min_score: Optional[float] = None,
                                        filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant documents for a query using vector similarity.

        Args:
            query: The search query
            selected_text: Optional selected text to prioritize in search
            top_k: Number of top results to return (defaults to config)
            min_score: Minimum similarity score threshold (defaults to config)
            filters: Optional filters to apply to the search

        Returns:
            List of relevant documents with metadata and similarity scores
        """
        start_time = time.time()

        # Use provided parameters or defaults
        top_k = top_k or self.top_k
        min_score = min_score or self.min_score

        try:
            # Generate embedding for the query
            embedding_result = await self.embedding_service.embed_question(query, selected_text)
            query_vector = embedding_result["embedding"]

            # Perform vector search
            search_results = self.qdrant_service.search_vectors(
                query_vector=query_vector,
                top_k=top_k * 2,  # Get more results than needed for filtering
                filters=filters
            )

            # Filter results by minimum score
            filtered_results = [
                result for result in search_results
                if result.get('score', 0) >= min_score
            ][:top_k]  # Take only top_k after filtering

            # Add metadata to results
            processed_results = []
            for result in filtered_results:
                payload = result.get('payload', {})
                processed_result = {
                    "id": result.get('id'),
                    "content": payload.get('content', ''),
                    "document_id": payload.get('document_id', ''),
                    "chapter": payload.get('chapter', ''),
                    "section_title": payload.get('section_title', ''),
                    "position": payload.get('position', 0),
                    "score": result.get('score', 0),
                    "metadata": payload.get('metadata', {}),
                    "relevance_score": result.get('score', 0)  # For compatibility
                }
                processed_results.append(processed_result)

            retrieval_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            logger.debug(f"Retrieved {len(processed_results)} documents in {retrieval_time:.2f}ms for query: {query[:50]}...")

            return processed_results

        except Exception as e:
            logger.error(f"Error retrieving documents for query '{query}': {e}")
            return []

    async def retrieve_by_document_ids(self, document_ids: List[str], query: str,
                                     top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve documents by specific document IDs using vector similarity within those documents.

        Args:
            document_ids: List of document IDs to search within
            query: The search query
            top_k: Number of top results to return

        Returns:
            List of relevant documents with metadata and similarity scores
        """
        start_time = time.time()
        top_k = top_k or self.top_k

        try:
            # Generate embedding for the query
            query_vector = await self.embedding_service.generate_embedding(query)

            # Search within specific documents
            results = []
            for doc_id in document_ids:
                doc_results = self.qdrant_service.search_by_document(doc_id, query_vector, top_k)
                for result in doc_results:
                    payload = result.get('payload', {})
                    processed_result = {
                        "id": result.get('id'),
                        "content": payload.get('content', ''),
                        "document_id": payload.get('document_id', ''),
                        "chapter": payload.get('chapter', ''),
                        "section_title": payload.get('section_title', ''),
                        "position": payload.get('position', 0),
                        "score": result.get('score', 0),
                        "metadata": payload.get('metadata', {})
                    }
                    results.append(processed_result)

            # Sort by score and return top results
            results.sort(key=lambda x: x['score'], reverse=True)
            final_results = results[:top_k]

            retrieval_time = (time.time() - start_time) * 1000
            logger.debug(f"Retrieved {len(final_results)} documents from specific IDs in {retrieval_time:.2f}ms")

            return final_results

        except Exception as e:
            logger.error(f"Error retrieving documents by IDs: {e}")
            return []

    async def retrieve_by_chapter(self, chapter: str, query: str,
                                top_k: Optional[int] = None, min_score: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Retrieve documents from a specific chapter using vector similarity.

        Args:
            chapter: Chapter name to search within
            query: The search query
            top_k: Number of top results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of relevant documents with metadata and similarity scores
        """
        start_time = time.time()
        top_k = top_k or self.top_k
        min_score = min_score or self.min_score

        try:
            # Generate embedding for the query
            query_vector = await self.embedding_service.generate_embedding(query)

            # Search within specific chapter
            search_results = self.qdrant_service.search_by_chapter(chapter, query_vector, top_k * 2)

            # Filter by minimum score
            filtered_results = [
                result for result in search_results
                if result.get('score', 0) >= min_score
            ][:top_k]

            # Process results
            processed_results = []
            for result in filtered_results:
                payload = result.get('payload', {})
                processed_result = {
                    "id": result.get('id'),
                    "content": payload.get('content', ''),
                    "document_id": payload.get('document_id', ''),
                    "chapter": payload.get('chapter', ''),
                    "section_title": payload.get('section_title', ''),
                    "position": payload.get('position', 0),
                    "score": result.get('score', 0),
                    "metadata": payload.get('metadata', {})
                }
                processed_results.append(processed_result)

            retrieval_time = (time.time() - start_time) * 1000
            logger.debug(f"Retrieved {len(processed_results)} documents from chapter '{chapter}' in {retrieval_time:.2f}ms")

            return processed_results

        except Exception as e:
            logger.error(f"Error retrieving documents by chapter '{chapter}': {e}")
            return []

    async def retrieve_with_selected_text_priority(self, query: str, selected_text: str,
                                                 top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve documents with priority given to those matching the selected text.

        Args:
            query: The search query
            selected_text: Text that was selected by the user (higher priority)
            top_k: Number of top results to return

        Returns:
            List of relevant documents with metadata and similarity scores
        """
        start_time = time.time()
        top_k = top_k or self.top_k

        try:
            # First, search for documents similar to the selected text
            if selected_text and selected_text.strip():
                # Search using just the selected text
                selected_text_embedding = await self.embedding_service.generate_embedding(selected_text)
                selected_text_results = self.qdrant_service.search_vectors(
                    query_vector=selected_text_embedding,
                    top_k=top_k
                )

                # Then search using the query
                query_embedding = await self.embedding_service.generate_embedding(query)
                query_results = self.qdrant_service.search_vectors(
                    query_vector=query_embedding,
                    top_k=top_k
                )

                # Combine and deduplicate results, giving priority to selected text matches
                combined_results = {}

                # Add selected text results with priority
                for result in selected_text_results:
                    combined_results[result.get('id')] = {
                        **result,
                        'priority_score': result.get('score', 0) * 1.1  # Boost selected text matches
                    }

                # Add query results, but don't overwrite selected text results
                for result in query_results:
                    result_id = result.get('id')
                    if result_id not in combined_results:
                        combined_results[result_id] = result
                        combined_results[result_id]['priority_score'] = result.get('score', 0)
                    else:
                        # If it's in both, use the higher score
                        current_score = combined_results[result_id]['priority_score']
                        new_score = result.get('score', 0)
                        combined_results[result_id]['priority_score'] = max(current_score, new_score)

                # Sort by priority score and return top results
                sorted_results = sorted(
                    combined_results.values(),
                    key=lambda x: x.get('priority_score', 0),
                    reverse=True
                )[:top_k]

                # Process results
                processed_results = []
                for result in sorted_results:
                    payload = result.get('payload', {})
                    processed_result = {
                        "id": result.get('id'),
                        "content": payload.get('content', ''),
                        "document_id": payload.get('document_id', ''),
                        "chapter": payload.get('chapter', ''),
                        "section_title": payload.get('section_title', ''),
                        "position": payload.get('position', 0),
                        "score": result.get('score', 0),
                        "priority_score": result.get('priority_score', 0),
                        "metadata": payload.get('metadata', {}),
                        "source": "selected_text" if result.get('priority_score', 0) > result.get('score', 0) * 1.05 else "query"
                    }
                    processed_results.append(processed_result)

            else:
                # If no selected text, just use regular retrieval
                processed_results = await self.retrieve_relevant_documents(query, top_k=top_k)

            retrieval_time = (time.time() - start_time) * 1000
            logger.debug(f"Retrieved {len(processed_results)} documents with selected text priority in {retrieval_time:.2f}ms")

            return processed_results

        except Exception as e:
            logger.error(f"Error retrieving documents with selected text priority: {e}")
            # Fall back to regular retrieval
            return await self.retrieve_relevant_documents(query, top_k=top_k)

    async def find_similar_documents(self, document_id: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find documents similar to a given document.

        Args:
            document_id: ID of the document to find similar documents for
            top_k: Number of top results to return

        Returns:
            List of similar documents with metadata and similarity scores
        """
        start_time = time.time()
        top_k = top_k or self.top_k

        try:
            # Get the document's chunks to find the one with highest position (most likely the main content)
            chunks = self.qdrant_service.get_chunks_by_document(document_id)

            if not chunks:
                logger.warning(f"No chunks found for document {document_id}")
                return []

            # Use the first chunk's content to generate a representative embedding
            # In a real implementation, you might want to use the most substantial chunk
            first_chunk = chunks[0]
            content = first_chunk.get('payload', {}).get('content', '')

            if not content:
                logger.warning(f"No content found in first chunk of document {document_id}")
                return []

            # Generate embedding for the content
            embedding = await self.embedding_service.generate_embedding(content)

            # Find similar documents (excluding the original document)
            search_results = self.qdrant_service.search_vectors(
                query_vector=embedding,
                top_k=top_k + 1  # Get one extra to exclude the original
            )

            # Filter out the original document and process results
            processed_results = []
            for result in search_results:
                result_doc_id = result.get('payload', {}).get('document_id', '')
                if result_doc_id != document_id:  # Exclude the original document
                    payload = result.get('payload', {})
                    processed_result = {
                        "id": result.get('id'),
                        "content": payload.get('content', '')[:200] + "..." if len(payload.get('content', '')) > 200 else payload.get('content', ''),
                        "document_id": result_doc_id,
                        "chapter": payload.get('chapter', ''),
                        "section_title": payload.get('section_title', ''),
                        "position": payload.get('position', 0),
                        "score": result.get('score', 0),
                        "metadata": payload.get('metadata', {})
                    }
                    processed_results.append(processed_result)

                    if len(processed_results) >= top_k:
                        break

            retrieval_time = (time.time() - start_time) * 1000
            logger.debug(f"Found {len(processed_results)} similar documents for {document_id} in {retrieval_time:.2f}ms")

            return processed_results

        except Exception as e:
            logger.error(f"Error finding similar documents for {document_id}: {e}")
            return []

    async def get_retrieval_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the retrieval service.

        Returns:
            Dictionary with retrieval statistics
        """
        qdrant_info = self.qdrant_service.get_collection_info()

        return {
            "qdrant_collection_info": qdrant_info,
            "default_top_k": self.top_k,
            "default_min_score": self.min_score,
            "status": "healthy" if qdrant_info else "unhealthy"
        }

    def rerank_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Rerank retrieval results based on additional criteria for better context selection.

        Args:
            results: List of retrieval results to rerank
            query: Original query for context

        Returns:
            Reranked list of results
        """
        # Enhanced reranking based on multiple factors for contextual learning support
        def calculate_rerank_score(result: Dict[str, Any]) -> float:
            content = result.get('content', '')
            original_score = result.get('score', 0)
            position = result.get('position', 0)
            metadata = result.get('metadata', {})

            # Calculate semantic relevance to query (basic keyword matching)
            query_lower = query.lower()
            content_lower = content.lower()

            # Count overlapping words between query and content
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            overlap_count = len(query_words.intersection(content_words))

            # Calculate keyword relevance score
            keyword_relevance = overlap_count / len(query_words) if query_words else 0

            # Content quality factors
            content_length = len(content)
            content_factor = min(content_length / 1500, 1.0)  # Normalize content length (optimal around 1500 chars)

            # Position factor (prefer earlier chunks but not too heavily penalized)
            position_factor = 1.0 / (1 + position * 0.1)  # Gentle position penalty

            # Recency factor if available in metadata (for contextual connections)
            recency_factor = 1.0
            if 'section_order' in metadata:
                # Higher section order might indicate more relevant information
                recency_factor = min(1.2, 1.0 + (metadata['section_order'] or 0) * 0.01)

            # Chapter relevance (if query seems related to a specific chapter)
            chapter_relevance = 1.0
            if 'chapter' in metadata and metadata['chapter']:
                chapter_lower = metadata['chapter'].lower()
                if any(term in chapter_lower for term in query_lower.split()):
                    chapter_relevance = 1.1  # Slight boost for relevant chapters

            # Calculate final rerank score with weighted components
            rerank_score = (
                (original_score * 0.4) +           # 40% weight to original vector similarity
                (keyword_relevance * 0.2) +        # 20% weight to keyword relevance
                (content_factor * 0.15) +          # 15% weight to content quality
                (position_factor * 0.1) +          # 10% weight to position
                (recency_factor * 0.08) +          # 8% weight to recency/section order
                (chapter_relevance * 0.07)         # 7% weight to chapter relevance
            )

            return rerank_score

        reranked_results = sorted(results, key=calculate_rerank_score, reverse=True)
        return reranked_results

    def rerank_for_contextual_learning(self, results: List[Dict[str, Any]], query: str,
                                     context_history: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Specialized reranking for contextual learning support that considers
        conversation history and related concepts.

        Args:
            results: List of retrieval results to rerank
            query: Current query
            context_history: Optional conversation history for contextual awareness

        Returns:
            Contextually reranked list of results
        """
        def calculate_contextual_rerank_score(result: Dict[str, Any]) -> float:
            content = result.get('content', '')
            original_score = result.get('score', 0)
            metadata = result.get('metadata', {})

            # Base score components (similar to regular reranking)
            query_lower = query.lower()
            content_lower = content.lower()

            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            overlap_count = len(query_words.intersection(content_words))
            keyword_relevance = overlap_count / len(query_words) if query_words else 0

            # Contextual factors
            contextual_score = original_score

            # If we have conversation history, boost results that connect to previous topics
            if context_history:
                for prev_context in context_history[-3:]:  # Look at last 3 context items
                    prev_content = prev_context.get('content', '').lower()
                    prev_content_words = set(prev_content.split())

                    # Boost if this result connects to previous conversation
                    connection_score = len(content_words.intersection(prev_content_words)) / max(len(content_words), 1)
                    if connection_score > 0.1:  # If there's some connection
                        contextual_score *= (1.0 + connection_score * 0.3)  # Up to 30% boost

            # Boost results that seem to contain explanations or examples
            explanation_keywords = ['example', 'example:', 'fig', 'fig.', 'figure', 'demonstrates', 'shows',
                                  'illustrates', 'case', 'scenario', 'application', 'practical']
            has_explanation = any(keyword in content_lower for keyword in explanation_keywords)
            if has_explanation:
                contextual_score *= 1.15  # 15% boost for explanation-rich content

            # Boost results that seem to provide foundational concepts
            concept_keywords = ['definition', 'define', 'concept', 'principle', 'fundamental',
                              'basic', 'introduction', 'overview', 'background']
            has_concept = any(keyword in content_lower for keyword in concept_keywords)
            if has_concept:
                contextual_score *= 1.1  # 10% boost for concept-rich content

            # Calculate final score combining all factors
            contextual_rerank_score = (
                (contextual_score * 0.5) +          # 50% weight to contextual score
                (keyword_relevance * 0.3) +         # 30% weight to keyword relevance
                (original_score * 0.2)              # 20% weight to original score as baseline
            )

            return contextual_rerank_score

        reranked_results = sorted(results, key=calculate_contextual_rerank_score, reverse=True)
        return reranked_results

    def assemble_context(self, retrieved_docs: List[Dict[str, Any]], query: str,
                        max_context_length: int = 2000, include_metadata: bool = True) -> Dict[str, Any]:
        """
        Assemble retrieved documents into a coherent context for the LLM.

        Args:
            retrieved_docs: List of retrieved documents with scores
            query: Original query for context
            max_context_length: Maximum length of the assembled context
            include_metadata: Whether to include metadata in the context

        Returns:
            Dictionary containing assembled context and metadata
        """
        if not retrieved_docs:
            return {
                "context": "",
                "sources": [],
                "context_length": 0,
                "truncated": False,
                "assembly_time": 0
            }

        start_time = time.time()

        # Sort documents by score to prioritize better matches
        sorted_docs = sorted(retrieved_docs, key=lambda x: x.get('score', 0), reverse=True)

        context_parts = []
        sources = []
        current_length = 0
        truncated = False

        for doc in sorted_docs:
            content = doc.get('content', '').strip()
            if not content:
                continue

            # Prepare document section with optional metadata
            doc_section = ""
            if include_metadata:
                doc_section = (
                    f"Document: {doc.get('document_id', 'Unknown')}\n"
                    f"Chapter: {doc.get('chapter', 'Unknown')}\n"
                    f"Section: {doc.get('section_title', 'Unknown')}\n"
                    f"Content:\n{content}\n\n"
                )
            else:
                doc_section = f"{content}\n\n"

            # Check if adding this document would exceed the max length
            if current_length + len(doc_section) > max_context_length:
                # Try to truncate this document to fit
                available_space = max_context_length - current_length
                if available_space > 0:
                    truncated_content = content[:available_space].rsplit(' ', 1)[0]  # Truncate at word boundary
                    if include_metadata:
                        doc_section = (
                            f"Document: {doc.get('document_id', 'Unknown')}\n"
                            f"Chapter: {doc.get('chapter', 'Unknown')}\n"
                            f"Section: {doc.get('section_title', 'Unknown')}\n"
                            f"Content:\n{truncated_content}...\n\n"
                        )
                    else:
                        doc_section = f"{truncated_content}...\n\n"

                    context_parts.append(doc_section)
                    current_length += len(doc_section)
                truncated = True
                break

            context_parts.append(doc_section)
            current_length += len(doc_section)

            # Add to sources
            sources.append({
                "document_id": doc.get('document_id'),
                "title": doc.get('section_title', ''),
                "url": doc.get('metadata', {}).get('url_path', ''),
                "score": doc.get('score', 0),
                "position": doc.get('position', 0)
            })

        # Combine all context parts
        assembled_context = "".join(context_parts).strip()

        assembly_time = (time.time() - start_time) * 1000

        return {
            "context": assembled_context,
            "sources": sources,
            "context_length": len(assembled_context),
            "truncated": truncated,
            "assembly_time_ms": assembly_time,
            "document_count": len(sources)
        }

    def format_context_for_llm(self, context_data: Dict[str, Any], query: str,
                              mode: str = "normal", system_prompt: Optional[str] = None) -> str:
        """
        Format the assembled context specifically for use with an LLM.

        Args:
            context_data: Output from assemble_context method
            query: The original query
            mode: The mode ("normal" or "selected-text")
            system_prompt: Optional system prompt to prepend

        Returns:
            Formatted context string ready for LLM consumption
        """
        context = context_data["context"]
        sources = context_data["sources"]

        # Create a formatted prompt for the LLM
        if mode == "selected-text":
            prompt_parts = [
                "You are a helpful assistant for the Physical AI & Humanoid Robotics textbook. ",
                "The user has selected specific text and asked a question about it. ",
                "Please answer the question based ONLY on the provided context, ",
                "focusing specifically on the selected text. If the answer is not in the provided context, ",
                "respond with: 'The answer is not found in the book.'\n\n"
            ]
        else:
            prompt_parts = [
                "You are a helpful assistant for the Physical AI & Humanoid Robotics textbook. ",
                "Please answer the user's question based ONLY on the provided context. ",
                "If the answer is not in the provided context, ",
                "respond with: 'The answer is not found in the book.'\n\n"
            ]

        # Add system prompt if provided
        if system_prompt:
            prompt_parts.insert(0, f"{system_prompt}\n\n")

        # Add the retrieved context
        prompt_parts.append(f"Context:\n{context}\n\n")

        # Add the query
        prompt_parts.append(f"Question: {query}\n\n")

        # Add sources information
        if sources:
            prompt_parts.append("Sources:\n")
            for i, source in enumerate(sources[:5]):  # Limit to top 5 sources
                prompt_parts.append(f"{i+1}. {source.get('title', 'Unknown')} ({source.get('document_id', 'Unknown')})\n")
            prompt_parts.append("\n")

        prompt_parts.append("Answer:")

        return "".join(prompt_parts)

    async def find_related_concepts(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find related concepts in the textbook that connect to the current query.

        Args:
            query: The current query or topic
            top_k: Number of related concepts to return

        Returns:
            List of related concepts with their connections
        """
        # First, get embeddings for the query
        query_embedding = await self.embedding_service.generate_embedding(query)

        # Search for semantically related content
        search_results = self.qdrant_service.search_vectors(
            query_vector=query_embedding,
            top_k=top_k * 3  # Get more results to find diverse concepts
        )

        # Process results to identify related concepts
        related_concepts = []
        seen_concepts = set()

        for result in search_results:
            content = result.get('payload', {}).get('content', '')
            if not content or len(content) < 50:  # Skip very short content
                continue

            # Extract potential concept keywords from the content
            concept_keywords = self._extract_concept_keywords(content, query)

            if concept_keywords and tuple(concept_keywords) not in seen_concepts:
                related_concepts.append({
                    "concept": result.get('payload', {}).get('section_title', 'Related Topic'),
                    "content": content[:300] + "..." if len(content) > 300 else content,
                    "document_id": result.get('payload', {}).get('document_id', ''),
                    "chapter": result.get('payload', {}).get('chapter', ''),
                    "similarity_score": result.get('score', 0),
                    "related_keywords": concept_keywords,
                    "connection_to_query": self._calculate_connection_strength(query, content)
                })
                seen_concepts.add(tuple(concept_keywords))

                if len(related_concepts) >= top_k:
                    break

        return related_concepts

    def _extract_concept_keywords(self, content: str, query: str) -> List[str]:
        """
        Extract potential concept keywords from content related to the query.

        Args:
            content: Text content to analyze
            query: Original query for context

        Returns:
            List of potential concept keywords
        """
        import re

        content_lower = content.lower()
        query_lower = query.lower()

        # Define common concept indicators in academic text
        concept_indicators = [
            r'\b(?:concept|principle|theory|model|algorithm|method|approach|technique|framework)\b',
            r'\b(?:definition|defined as|is defined as)\b',
            r'\b(?:consist of|comprises|includes|contains)\b',
            r'\b(?:characteristic|feature|property|aspect|element)\b',
            r'\b(?:type|kind|category|class|group)\b',
            r'\b(?:example|instance|case|application|use|implementation)\b'
        ]

        # Look for concept-indicating phrases
        concept_keywords = []
        for indicator in concept_indicators:
            matches = re.findall(indicator, content_lower)
            if matches:
                # Extract surrounding context that might contain the concept name
                for match in re.finditer(indicator, content_lower):
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end]

                    # Look for capitalized terms or terms in quotes near the indicator
                    concept_match = re.search(r'"([^"]+)"|\'([^\']+)\'|([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', context)
                    if concept_match:
                        concept = concept_match.group(1) or concept_match.group(2) or concept_match.group(3)
                        if concept and len(concept) > 2 and concept.lower() not in [q.lower() for q in query.split()]:
                            concept_keywords.append(concept.strip())

        # If no specific concepts found, use key terms from the content
        if not concept_keywords:
            # Simple keyword extraction based on frequency and relevance
            words = re.findall(r'\b[a-zA-Z]{4,}\b', content_lower)
            word_freq = {}
            for word in words:
                if word not in ['that', 'with', 'from', 'this', 'have', 'will', 'been', 'also', 'their', 'they', 'which', 'when', 'where', 'what', 'how', 'who', 'why']:
                    word_freq[word] = word_freq.get(word, 0) + 1

            # Get top 3 most frequent terms
            top_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
            concept_keywords = [term[0] for term in top_terms if term[0] not in query_lower]

        return concept_keywords[:3]  # Return top 3 concept keywords

    async def find_concept_connections(self, concept1: str, concept2: str) -> Dict[str, Any]:
        """
        Find connections between two concepts in the textbook.

        Args:
            concept1: First concept to connect
            concept2: Second concept to connect

        Returns:
            Dictionary with connection information
        """
        # Get embeddings for both concepts
        concept1_embedding = await self.embedding_service.generate_embedding(concept1)
        concept2_embedding = await self.embedding_service.generate_embedding(concept2)

        # Find content that mentions both concepts
        results1 = self.qdrant_service.search_vectors(
            query_vector=concept1_embedding,
            top_k=10
        )

        results2 = self.qdrant_service.search_vectors(
            query_vector=concept2_embedding,
            top_k=10
        )

        # Look for overlapping content that connects both concepts
        connections = []
        concept1_content = {r['id']: r for r in results1}

        for result2 in results2:
            result2_id = result2['id']
            if result2_id in concept1_content:
                # Found content that's relevant to both concepts
                content = result2.get('payload', {}).get('content', '')
                connections.append({
                    "content": content,
                    "document_id": result2.get('payload', {}).get('document_id', ''),
                    "chapter": result2.get('payload', {}).get('chapter', ''),
                    "section_title": result2.get('payload', {}).get('section_title', ''),
                    "connection_strength": (result2.get('score', 0) + concept1_content[result2_id].get('score', 0)) / 2
                })

        # If no direct connections found, look for indirect connections
        if not connections:
            # Find content that might bridge the two concepts
            combined_query = f"{concept1} {concept2}"
            combined_embedding = await self.embedding_service.generate_embedding(combined_query)

            bridge_results = self.qdrant_service.search_vectors(
                query_vector=combined_embedding,
                top_k=5
            )

            for result in bridge_results:
                content = result.get('payload', {}).get('content', '')
                connections.append({
                    "content": content,
                    "document_id": result.get('payload', {}).get('document_id', ''),
                    "chapter": result.get('payload', {}).get('chapter', ''),
                    "section_title": result.get('payload', {}).get('section_title', ''),
                    "connection_strength": result.get('score', 0),
                    "type": "potential_bridge"
                })

        return {
            "concept1": concept1,
            "concept2": concept2,
            "connections": connections,
            "connection_count": len(connections)
        }

    def _calculate_connection_strength(self, query: str, content: str) -> float:
        """
        Calculate how strongly the content connects to the query.

        Args:
            query: The original query
            content: Content to evaluate

        Returns:
            Connection strength score (0.0 to 1.0)
        """
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        # Calculate overlap
        overlap = len(query_words.intersection(content_words))
        total_unique = len(query_words.union(content_words))

        if total_unique == 0:
            return 0.0

        # Jaccard similarity
        jaccard = overlap / total_unique

        # Also consider word embedding similarity for semantic connection
        # For now, using a simple approach; in production, you'd use embeddings
        return min(1.0, jaccard * 2)  # Boost the score slightly as baseline

    def create_context_summary(self, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a summary of the retrieved context for monitoring and analysis.

        Args:
            retrieved_docs: List of retrieved documents

        Returns:
            Dictionary with context summary statistics
        """
        if not retrieved_docs:
            return {
                "document_count": 0,
                "total_content_length": 0,
                "average_score": 0,
                "max_score": 0,
                "min_score": 0,
                "unique_chapters": [],
                "coverage_score": 0
            }

        content_lengths = []
        scores = []
        chapters = set()
        doc_ids = set()

        for doc in retrieved_docs:
            content = doc.get('content', '')
            content_lengths.append(len(content))
            scores.append(doc.get('score', 0))
            chapters.add(doc.get('chapter', 'Unknown'))
            doc_ids.add(doc.get('document_id'))

        total_content_length = sum(content_lengths)
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0

        # Calculate coverage score (how diverse the results are)
        coverage_score = len(chapters) / len(retrieved_docs) if retrieved_docs else 0

        return {
            "document_count": len(retrieved_docs),
            "unique_document_count": len(doc_ids),
            "total_content_length": total_content_length,
            "average_content_length": total_content_length / len(retrieved_docs) if retrieved_docs else 0,
            "average_score": avg_score,
            "max_score": max_score,
            "min_score": min_score,
            "unique_chapters": list(chapters),
            "unique_chapters_count": len(chapters),
            "coverage_score": coverage_score
        }

    def validate_context_grounding(self, context: str, answer: str) -> Dict[str, Any]:
        """
        Validate that the answer is properly grounded in the provided context.

        Args:
            context: The context provided to the LLM
            answer: The answer generated by the LLM

        Returns:
            Dictionary with grounding validation results
        """
        # This is a simplified grounding validation
        # In a production system, you might use more sophisticated NLP techniques

        # Check if the answer contains content that appears in the context
        context_lower = context.lower()
        answer_lower = answer.lower()

        # Count overlapping words
        context_words = set(context_lower.split())
        answer_words = set(answer_lower.split())

        overlapping_words = context_words.intersection(answer_words)
        overlap_count = len(overlapping_words)

        # Calculate overlap ratio
        if len(answer_words) > 0:
            overlap_ratio = overlap_count / len(answer_words)
        else:
            overlap_ratio = 0

        # Check for specific phrases that indicate proper grounding
        not_found_indicators = ["not found in the book", "no information", "no relevant"]
        is_not_found_response = any(indicator in answer_lower for indicator in not_found_indicators)

        return {
            "is_properly_grounded": overlap_ratio > 0.1 or is_not_found_response,  # At least 10% overlap or "not found" response
            "overlap_ratio": overlap_ratio,
            "overlap_word_count": overlap_count,
            "is_not_found_response": is_not_found_response,
            "grounding_score": overlap_ratio if not is_not_found_response else 1.0,
            "validation_notes": "Answer appears grounded in context" if overlap_ratio > 0.1 else "Low overlap detected"
        }


# Singleton instance
retrieval_service = RetrievalService()


async def main():
    """Main function to demonstrate retrieval service usage."""
    service = RetrievalService()

    # Example: Test retrieval with a sample query
    print("Testing retrieval service...")

    # This would normally require a populated Qdrant database
    # For demonstration, we'll show the method signatures
    sample_query = "What is artificial intelligence in robotics?"

    print(f"Sample query: {sample_query}")
    print("Note: Actual retrieval requires a populated Qdrant database with textbook content.")

    # Show the available methods
    stats = await service.get_retrieval_statistics()
    print(f"Retrieval service stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())