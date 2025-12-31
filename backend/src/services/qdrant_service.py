"""
Qdrant Service for RAG System

This module handles all interactions with the Qdrant vector database,
including collection setup, vector operations, and similarity search.
"""
from typing import List, Dict, Optional, Any, Tuple
from uuid import uuid4
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PayloadSchemaType
from pydantic import BaseModel

from src.config.settings import settings
from src.models.document import DocumentChunk


logger = logging.getLogger(__name__)


class QdrantPayloadSchema(BaseModel):
    """Schema for Qdrant payload fields."""
    content: str
    document_id: str
    chapter: str
    section_title: str
    position: int
    metadata: Dict[str, Any]


class QdrantService:
    """Service class for interacting with Qdrant vector database."""

    def __init__(self):
        """Initialize Qdrant client and set collection name."""
        # Use local persistent mode to maintain data between runs
        print("Starting Qdrant in local persistent mode...")
        self.client = QdrantClient(path="./qdrant_data")  # Local file-based storage
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    def create_collection(self) -> bool:
        """
        Create Qdrant collection with specified schema.

        Returns:
            True if collection was created, False if it already exists
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]

            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return False

            # Create collection with specified vector size and configuration
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_VECTOR_SIZE,  # 1536 for OpenAI ada-002
                    distance=Distance.COSINE
                )
            )

            # Create payload indexes for faster filtering and searching
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="document_id",
                field_schema=PayloadSchemaType.KEYWORD
            )

            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="chapter",
                field_schema=PayloadSchemaType.KEYWORD
            )

            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="section_title",
                field_schema=PayloadSchemaType.TEXT
            )

            logger.info(f"Collection '{self.collection_name}' created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating collection '{self.collection_name}': {e}")
            raise

    def delete_collection(self) -> bool:
        """
        Delete the Qdrant collection.

        Returns:
            True if collection was deleted, False otherwise
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Collection '{self.collection_name}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection '{self.collection_name}': {e}")
            return False

    def recreate_collection(self) -> bool:
        """
        Delete and recreate the Qdrant collection.

        Returns:
            True if collection was recreated, False otherwise
        """
        # Delete existing collection if it exists
        self.delete_collection()

        # Create new collection
        return self.create_collection()

    def add_vectors(self, vectors: List[List[float]], payloads: List[Dict[str, Any]],
                   ids: Optional[List[str]] = None) -> bool:
        """
        Add vectors with payloads to the collection.

        Args:
            vectors: List of embedding vectors
            payloads: List of payload dictionaries
            ids: Optional list of IDs for the vectors

        Returns:
            True if vectors were added successfully, False otherwise
        """
        try:
            if ids is None:
                # Generate random UUIDs if no IDs provided
                ids = [str(uuid4()) for _ in range(len(vectors))]

            # Validate that all lists have the same length
            if not (len(vectors) == len(payloads) == len(ids)):
                raise ValueError("Vectors, payloads, and ids must have the same length")

            # Check if collection exists, create it if it doesn't
            try:
                self.client.get_collection(self.collection_name)
            except:
                logger.info(f"Collection '{self.collection_name}' not found, creating it...")
                self.create_collection()

            # Add points to collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=models.Batch(
                    ids=ids,
                    vectors=vectors,
                    payloads=payloads
                )
            )

            logger.info(f"Added {len(vectors)} vectors to collection '{self.collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error adding vectors to collection: {e}")
            raise

    def add_document_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> bool:
        """
        Add document chunks with their embeddings to the collection.

        Args:
            chunks: List of DocumentChunk objects
            embeddings: List of embedding vectors corresponding to the chunks

        Returns:
            True if chunks were added successfully, False otherwise
        """
        try:
            # Validate that chunks and embeddings have the same length
            if len(chunks) != len(embeddings):
                raise ValueError("Number of chunks must match number of embeddings")

            # Prepare vectors and payloads
            vectors = embeddings
            payloads = []

            for chunk in chunks:
                payload = {
                    "content": chunk.content,
                    "document_id": chunk.document_id,
                    "chapter": chunk.chapter,
                    "section_title": chunk.section_title,
                    "position": chunk.position,
                    "metadata": chunk.metadata
                }
                payloads.append(payload)

            # Generate IDs based on document_id and position
            ids = [f"{chunk.document_id}_pos_{chunk.position}" for chunk in chunks]

            return self.add_vectors(vectors, payloads, ids)

        except Exception as e:
            logger.error(f"Error adding document chunks to collection: {e}")
            raise

    def search_vectors(self, query_vector: List[float], top_k: int = 5,
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the collection.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filters: Optional filters for search

        Returns:
            List of matching points with payload and score
        """
        try:
            # Prepare filters if provided
            qdrant_filters = None
            if filters:
                filter_conditions = []

                for key, value in filters.items():
                    if isinstance(value, list):
                        # Handle list of values (OR condition)
                        conditions = [models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=v)
                        ) for v in value]
                        filter_conditions.append(models.ShouldCondition(
                            should=conditions
                        ))
                    else:
                        # Handle single value
                        filter_conditions.append(models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        ))

                if filter_conditions:
                    qdrant_filters = models.Filter(
                        must=filter_conditions
                    )

            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=qdrant_filters,
                with_payload=True,
                with_vectors=False
            )

            # Format results
            results = []
            for result in search_results:
                formatted_result = {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                results.append(formatted_result)

            return results

        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            raise

    def search_by_document(self, document_id: str, query_vector: List[float],
                          top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar vectors within a specific document.

        Args:
            document_id: ID of the document to search within
            query_vector: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of matching points from the specified document
        """
        filters = {"document_id": document_id}
        return self.search_vectors(query_vector, top_k, filters)

    def search_by_chapter(self, chapter: str, query_vector: List[float],
                         top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar vectors within a specific chapter.

        Args:
            chapter: Name of the chapter to search within
            query_vector: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of matching points from the specified chapter
        """
        filters = {"chapter": chapter}
        return self.search_vectors(query_vector, top_k, filters)

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific chunk by its ID.

        Args:
            chunk_id: ID of the chunk to retrieve

        Returns:
            Chunk data if found, None otherwise
        """
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[chunk_id],
                with_payload=True,
                with_vectors=False
            )

            if points and len(points) > 0:
                point = points[0]
                return {
                    "id": point.id,
                    "payload": point.payload
                }
            return None

        except Exception as e:
            logger.error(f"Error retrieving chunk by ID: {e}")
            return None

    def get_chunks_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks for a specific document.

        Args:
            document_id: ID of the document

        Returns:
            List of chunks for the document
        """
        try:
            # Create filter for document_id
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id)
                    )
                ]
            )

            points = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=10000,  # Adjust as needed
                with_payload=True,
                with_vectors=False
            )

            results = []
            for point in points[0]:  # points is a tuple (records, next_page_offset)
                results.append({
                    "id": point.id,
                    "payload": point.payload
                })

            return results

        except Exception as e:
            logger.error(f"Error retrieving chunks by document ID: {e}")
            return []

    def delete_by_document_id(self, document_id: str) -> bool:
        """
        Delete all vectors associated with a specific document.

        Args:
            document_id: ID of the document to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Create filter for document_id
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id)
                    )
                ]
            )

            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=filter_condition
                )
            )

            logger.info(f"Deleted all chunks for document '{document_id}'")
            return True

        except Exception as e:
            logger.error(f"Error deleting chunks by document ID: {e}")
            return False

    def update_vectors(self, ids: List[str], vectors: Optional[List[List[float]]] = None,
                      payloads: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Update existing vectors and/or payloads in the collection.

        Args:
            ids: List of IDs of vectors to update
            vectors: Optional list of new embedding vectors
            payloads: Optional list of new payload dictionaries

        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Prepare the update operation
            points = []
            for i, point_id in enumerate(ids):
                point = models.PointStruct(
                    id=point_id,
                    vector=vectors[i] if vectors else None,
                    payload=payloads[i] if payloads else None
                )
                points.append(point)

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            logger.info(f"Updated {len(ids)} vectors in collection '{self.collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error updating vectors: {e}")
            raise

    def batch_search(self, query_vectors: List[List[float]], top_k: int = 5,
                    filters: Optional[Dict[str, Any]] = None) -> List[List[Dict[str, Any]]]:
        """
        Perform batch search with multiple query vectors.

        Args:
            query_vectors: List of query embedding vectors
            top_k: Number of results to return for each query
            filters: Optional filters for search

        Returns:
            List of lists, each containing matching points for the corresponding query
        """
        try:
            # Prepare filters if provided
            qdrant_filters = None
            if filters:
                filter_conditions = []

                for key, value in filters.items():
                    if isinstance(value, list):
                        # Handle list of values (OR condition)
                        conditions = [models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=v)
                        ) for v in value]
                        filter_conditions.append(models.ShouldCondition(
                            should=conditions
                        ))
                    else:
                        # Handle single value
                        filter_conditions.append(models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        ))

                if filter_conditions:
                    qdrant_filters = models.Filter(
                        must=filter_conditions
                    )

            # Perform batch search
            search_requests = [
                models.SearchRequest(
                    vector=query_vector,
                    limit=top_k,
                    filter=qdrant_filters,
                    with_payload=True,
                    with_vectors=False
                )
                for query_vector in query_vectors
            ]

            results = self.client.search_batch(
                collection_name=self.collection_name,
                requests=search_requests
            )

            # Format results
            formatted_results = []
            for result_list in results:
                formatted_result_list = []
                for result in result_list:
                    formatted_result = {
                        "id": result.id,
                        "score": result.score,
                        "payload": result.payload
                    }
                    formatted_result_list.append(formatted_result)
                formatted_results.append(formatted_result_list)

            return formatted_results

        except Exception as e:
            logger.error(f"Error performing batch search: {e}")
            raise

    def get_vector_by_id(self, point_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a vector by its ID.

        Args:
            point_id: ID of the point to retrieve

        Returns:
            Point data if found, None otherwise
        """
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
                with_payload=True,
                with_vectors=True  # Include vectors
            )

            if points and len(points) > 0:
                point = points[0]
                return {
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload
                }
            return None

        except Exception as e:
            logger.error(f"Error retrieving vector by ID: {e}")
            return None

    def get_vectors_by_ids(self, point_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve multiple vectors by their IDs.

        Args:
            point_ids: List of IDs of points to retrieve

        Returns:
            List of point data
        """
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=point_ids,
                with_payload=True,
                with_vectors=True  # Include vectors
            )

            results = []
            for point in points:
                results.append({
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload
                })

            return results

        except Exception as e:
            logger.error(f"Error retrieving vectors by IDs: {e}")
            return []

    def scroll_collection(self, limit: int = 100, offset: Optional[str] = None,
                         filters: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Scroll through the collection to retrieve all points.

        Args:
            limit: Number of points to retrieve
            offset: Offset for pagination
            filters: Optional filters for scrolling

        Returns:
            Tuple of (list of points, next offset)
        """
        try:
            # Prepare filters if provided
            qdrant_filter = None
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        # Handle list of values (OR condition)
                        conditions = [models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=v)
                        ) for v in value]
                        filter_conditions.append(models.ShouldCondition(
                            should=conditions
                        ))
                    else:
                        # Handle single value
                        filter_conditions.append(models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        ))

                if filter_conditions:
                    qdrant_filter = models.Filter(
                        must=filter_conditions
                    )

            records, next_offset = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=qdrant_filter,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            results = []
            for record in records:
                results.append({
                    "id": record.id,
                    "payload": record.payload
                })

            return results, next_offset

        except Exception as e:
            logger.error(f"Error scrolling collection: {e}")
            return [], None

    def count_points_with_filters(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count the number of points in the collection with optional filters.

        Args:
            filters: Optional filters for counting

        Returns:
            Number of points matching the filters
        """
        try:
            # Prepare filters if provided
            qdrant_filter = None
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        # Handle list of values (OR condition)
                        conditions = [models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=v)
                        ) for v in value]
                        filter_conditions.append(models.ShouldCondition(
                            should=conditions
                        ))
                    else:
                        # Handle single value
                        filter_conditions.append(models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        ))

                if filter_conditions:
                    qdrant_filter = models.Filter(
                        must=filter_conditions
                    )

            count_result = self.client.count(
                collection_name=self.collection_name,
                count_filter=qdrant_filter
            )

            return count_result.count

        except Exception as e:
            logger.error(f"Error counting points: {e}")
            return 0

    def recommend_vectors(self, positive_ids: List[str], negative_ids: Optional[List[str]] = None,
                         top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Recommend vectors similar to positive examples and dissimilar to negative examples.

        Args:
            positive_ids: List of IDs of positive examples
            negative_ids: Optional list of IDs of negative examples
            top_k: Number of results to return
            filters: Optional filters for search

        Returns:
            List of recommended points with payload and score
        """
        try:
            # Prepare filters if provided
            qdrant_filters = None
            if filters:
                filter_conditions = []

                for key, value in filters.items():
                    if isinstance(value, list):
                        # Handle list of values (OR condition)
                        conditions = [models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=v)
                        ) for v in value]
                        filter_conditions.append(models.ShouldCondition(
                            should=conditions
                        ))
                    else:
                        # Handle single value
                        filter_conditions.append(models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        ))

                if filter_conditions:
                    qdrant_filters = models.Filter(
                        must=filter_conditions
                    )

            # Perform recommendation
            results = self.client.recommend(
                collection_name=self.collection_name,
                positive=positive_ids,
                negative=negative_ids or [],
                limit=top_k,
                filter=qdrant_filters,
                with_payload=True,
                with_vectors=False
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                formatted_results.append(formatted_result)

            return formatted_results

        except Exception as e:
            logger.error(f"Error performing recommendation: {e}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Dictionary with collection information
        """
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": collection_info.config.params.vectors.size,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "point_count": collection_info.points_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}

    def count_points(self) -> int:
        """
        Count the number of points in the collection.

        Returns:
            Number of points in the collection
        """
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            return collection_info.points_count
        except Exception as e:
            logger.error(f"Error counting points: {e}")
            return 0

    def health_check(self) -> bool:
        """
        Check if Qdrant service is healthy.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Try to get collections to verify connection
            self.client.get_collections()
            return True
        except Exception:
            return False


# Singleton instance
qdrant_service = QdrantService()


def main():
    """Main function to demonstrate Qdrant service usage."""
    # Initialize service
    service = QdrantService()

    # Example: Create collection
    print("Creating Qdrant collection...")
    created = service.create_collection()
    if created:
        print("Collection created successfully!")
    else:
        print("Collection already exists or creation failed.")

    # Example: Get collection info
    info = service.get_collection_info()
    print(f"Collection info: {info}")

    # Example: Check health
    healthy = service.health_check()
    print(f"Service health: {'Healthy' if healthy else 'Unhealthy'}")


if __name__ == "__main__":
    main()