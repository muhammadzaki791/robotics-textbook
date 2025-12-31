#!/usr/bin/env python3
"""
Test script to verify RAG functionality works with ingested content
"""
import asyncio
import sys
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.qdrant_service import qdrant_service
from src.services.embedding_service import embedding_service
from src.services.retrieval_service import retrieval_service
from src.services.ingestion_service import ingestion_service
from src.models.document import DocumentChunk
from uuid import uuid4


async def test_qdrant_connection():
    """Test that Qdrant service is working and has ingested content."""
    print("Testing Qdrant connection...")

    # Check if collection exists
    try:
        collection_info = qdrant_service.get_collection_info()
        print(f"Collection info: {collection_info}")

        # Count points in collection
        count = qdrant_service.count_points()
        print(f"Number of points in collection: {count}")

        if count > 0:
            print("SUCCESS: Qdrant has ingested content!")
            return True
        else:
            print("ERROR: Qdrant collection is empty")
            return False
    except Exception as e:
        print(f"ERROR: Error accessing Qdrant: {e}")
        return False


async def test_embedding_generation():
    """Test that embedding service works."""
    print("\nTesting embedding generation...")

    try:
        test_text = "What are humanoid robots?"
        embeddings = await embedding_service.generate_embeddings([test_text])

        if len(embeddings) > 0 and len(embeddings[0]) > 0:
            print(f"SUCCESS: Embedding generated successfully, vector size: {len(embeddings[0])}")
            return True
        else:
            print("ERROR: Failed to generate embedding")
            return False
    except Exception as e:
        print(f"ERROR: Error generating embedding: {e}")
        return False


async def test_retrieval():
    """Test that retrieval service can find relevant content."""
    print("\nTesting content retrieval...")

    try:
        # Test query
        test_query = "What are the key concepts in humanoid robotics?"

        # Perform retrieval
        results = await retrieval_service.retrieve_context(test_query)

        print(f"Retrieved {len(results)} relevant chunks")
        if len(results) > 0:
            print(f"First result score: {results[0]['score']:.4f}")
            print(f"First result content preview: {results[0]['content'][:100]}...")
            print("SUCCESS: Retrieval service working!")
            return True
        else:
            print("ERROR: No results retrieved")
            return False
    except Exception as e:
        print(f"ERROR: Error during retrieval: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("Testing RAG functionality after ingestion...")
    print("="*50)

    # Test 1: Qdrant connection
    qdrant_ok = await test_qdrant_connection()

    # Test 2: Embedding generation
    embedding_ok = await test_embedding_generation()

    # Test 3: Content retrieval
    retrieval_ok = await test_retrieval()

    print("\n" + "="*50)
    print("Test Results:")
    print(f"  Qdrant Connection: {'SUCCESS' if qdrant_ok else 'ERROR'}")
    print(f"  Embedding Service: {'SUCCESS' if embedding_ok else 'ERROR'}")
    print(f"  Retrieval Service: {'SUCCESS' if retrieval_ok else 'ERROR'}")

    if qdrant_ok and embedding_ok and retrieval_ok:
        print("\nSUCCESS: All RAG functionality tests passed! The system should now be able to answer questions from the textbook.")
        return True
    else:
        print("\nERROR: Some tests failed. Please check the services.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)