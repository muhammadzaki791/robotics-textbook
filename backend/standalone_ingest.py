#!/usr/bin/env python3
"""
Standalone Ingestion Script for Textbook Chunks with Rate Limiting

This script loads the chunked textbook content from JSON and ingests it into the
Qdrant vector database with proper rate limiting to avoid API errors.
This version creates its own Qdrant client to avoid file locking issues.
"""
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from uuid import uuid4

# Add the src directory to the path so we can import our services
sys.path.insert(0, str(Path(__file__).parent))

from src.models.document import DocumentChunk
from src.config.settings import settings
from src.services.embedding_service import EmbeddingService
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import Distance, VectorParams
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StandaloneQdrantService:
    """Standalone Qdrant service for ingestion without singleton conflicts."""

    def __init__(self):
        """Initialize Qdrant client with persistent storage."""
        print("Starting Qdrant in local persistent mode for ingestion...")
        self.client = QdrantClient(path="./qdrant_data")
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    def create_collection(self) -> bool:
        """
        Create Qdrant collection with specified schema.

        Returns:
            True if collection was created, False if it already exists
        """
        try:
            # Check if collection already exists
            collections_response = self.client.get_collections()
            existing_collections = [col.name for col in collections_response.collections]

            if self.collection_name in existing_collections:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return False

            # Create collection with vector configuration
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIM,  # Use the configured embedding dimension
                    distance=Distance.COSINE
                )
            )

            logger.info(f"Created collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise

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

    def count_points(self) -> int:
        """Count the number of points in the collection."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count
        except:
            return 0


class StandaloneIngestionService:
    """Standalone ingestion service without singleton dependencies."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.qdrant_service = StandaloneQdrantService()

    async def ingest_document_chunks(self, document_chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Ingest document chunks into the vector database with detailed error handling.

        Args:
            document_chunks: List of DocumentChunk objects to ingest

        Returns:
            Dictionary with ingestion results
        """
        start_time = time.time()

        # Extract text content for embedding generation
        texts = [chunk.content for chunk in document_chunks]
        document_ids = [chunk.id for chunk in document_chunks]

        # Generate embeddings for all chunks
        print(f"Generating embeddings for {len(texts)} chunks...")

        # Process in smaller batches to avoid rate limits
        embeddings = []
        batch_size = 3  # Very small batch size to respect API limits
        total_chunks = len(texts)

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(texts) - 1) // batch_size + 1

            print(f"Processing embedding batch {batch_num}/{total_batches} ({len(batch)} items)...")

            try:
                batch_embeddings = await self.embedding_service.generate_embeddings(batch)
                embeddings.extend(batch_embeddings)

                # Add delay between batches to respect rate limits
                print("Waiting 2 seconds between batches...")
                await asyncio.sleep(2)

            except Exception as e:
                print(f"Error processing batch {batch_num}: {e}")
                print("Waiting 5 seconds before continuing...")
                await asyncio.sleep(5)
                # Continue with next batch instead of failing completely

        print(f"Generated {len(embeddings)} embeddings")

        # Prepare payloads for Qdrant
        payloads = []
        for chunk in document_chunks:
            payload = {
                "content": chunk.content,
                "document_id": chunk.document_id,
                "chapter": chunk.chapter,
                "section_title": chunk.section_title,
                "position": chunk.position,
                "token_count": chunk.token_count,
                "metadata": chunk.metadata
            }
            payloads.append(payload)

        # Generate IDs for Qdrant (use UUID for valid format)
        ids = [str(uuid4()) for _ in document_chunks]

        # Add vectors to Qdrant
        print("Adding vectors to Qdrant database...")
        qdrant_success = self.qdrant_service.add_vectors(
            vectors=embeddings,
            payloads=payloads,
            ids=ids
        )

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Prepare result
        result = {
            "status": "success" if qdrant_success else "partial_success",
            "message": f"Successfully ingested {len(document_chunks)} chunks",
            "total_chunks": len(document_chunks),
            "processed_chunks": len(document_chunks),
            "failed_chunks": 0,  # We don't track individual failures in this simplified version
            "processing_time_ms": processing_time,
            "qdrant_success": qdrant_success
        }

        return result


async def load_chunks_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Load chunks from the JSON file created by the chunking process.

    Args:
        file_path: Path to the JSON file containing chunks

    Returns:
        List of chunk dictionaries
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        chunks_data = json.load(f)

    print(f"Loaded {len(chunks_data)} chunks from {file_path}")
    return chunks_data


async def convert_to_document_chunks(chunks_data: List[Dict[str, Any]]) -> List[DocumentChunk]:
    """
    Convert chunk dictionaries to DocumentChunk objects.

    Args:
        chunks_data: List of chunk dictionaries

    Returns:
        List of DocumentChunk objects
    """
    document_chunks = []

    for chunk_data in chunks_data:
        chunk = DocumentChunk(
            id=chunk_data.get('id', str(uuid4())),
            content=chunk_data['content'],
            document_id=chunk_data['document_id'],
            chapter=chunk_data['chapter'],
            section_title=chunk_data.get('section_title', ''),
            position=chunk_data.get('position', 0),
            token_count=chunk_data.get('token_count'),
            metadata=chunk_data.get('metadata', {})
        )
        document_chunks.append(chunk)

    return document_chunks


async def main():
    """Main function to ingest textbook chunks into the RAG system with rate limiting."""
    print("Starting standalone batched textbook content ingestion process...")

    # Path to the chunks JSON file created by process_textbook_chunks.py
    chunks_file = "textbook_chunks.json"

    if not Path(chunks_file).exists():
        print(f"Error: {chunks_file} not found!")
        print("Please run process_textbook_chunks.py first to generate the chunks.")
        return 1

    try:
        # Load chunks from JSON file
        print("Loading chunks from JSON file...")
        chunks_data = await load_chunks_from_json(chunks_file)

        # Convert to DocumentChunk objects
        print("Converting chunks to DocumentChunk objects...")
        document_chunks = await convert_to_document_chunks(chunks_data)

        print(f"Converted {len(document_chunks)} chunks for ingestion")

        # Create standalone ingestion service (no singleton conflicts)
        ingestion_service = StandaloneIngestionService()

        # Perform ingestion
        print("Starting ingestion into vector database...")
        result = await ingestion_service.ingest_document_chunks(document_chunks)

        print(f"Ingestion completed with result: {result}")

        if result['status'] == 'success':
            print(f"Successfully ingested {result['processed_chunks']} chunks")
            if result['failed_chunks'] > 0:
                print(f"Warning: {result['failed_chunks']} chunks failed to ingest")

            print(f"Processing time: {result['processing_time_ms']:.2f}ms")

            # Check final count
            final_count = ingestion_service.qdrant_service.count_points()
            print(f"Total vectors in database: {final_count}")

            print("Textbook content is now available for RAG queries!")
            return 0
        else:
            print(f"Ingestion failed: {result['message']}")
            return 1

    except Exception as e:
        print(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)