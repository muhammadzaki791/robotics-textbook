"""
Vector Search and Nearest-Neighbor Query Testing

This module tests the basic vector search and nearest-neighbor query functionality
of the RAG system using the Qdrant vector database.
"""
import asyncio
import random
from typing import List, Dict, Any
import logging
import time

from src.services.qdrant_service import qdrant_service
from src.services.embedding_service import embedding_service
from src.models.database import get_db
from src.services.postgres_service import postgres_service


logger = logging.getLogger(__name__)


class VectorSearchTester:
    """Class to test vector search and nearest-neighbor query functionality."""

    def __init__(self):
        """Initialize the vector search tester."""
        self.qdrant_service = qdrant_service
        self.embedding_service = embedding_service
        self.postgres_service = postgres_service

    async def create_test_collection(self, collection_name: str = "test_textbook_content") -> bool:
        """
        Create a test collection for vector search testing.

        Args:
            collection_name: Name of the test collection

        Returns:
            True if collection was created successfully, False otherwise
        """
        try:
            # Set the collection name for testing
            self.qdrant_service.collection_name = collection_name

            # Create the collection
            created = self.qdrant_service.create_collection()
            if created:
                logger.info(f"Test collection '{collection_name}' created successfully")
            else:
                logger.info(f"Test collection '{collection_name}' already exists")

            return True
        except Exception as e:
            logger.error(f"Error creating test collection: {e}")
            return False

    async def add_test_vectors(self, num_vectors: int = 10) -> bool:
        """
        Add test vectors to the collection for search testing.

        Args:
            num_vectors: Number of test vectors to add

        Returns:
            True if vectors were added successfully, False otherwise
        """
        try:
            # Create test content
            test_texts = [
                f"This is test document {i} about robotics and artificial intelligence. " +
                "Robotics is an interdisciplinary field that integrates mechanical engineering, " +
                "electrical engineering, and computer science to design, construct, operate, " +
                "and use robots." for i in range(num_vectors)
            ]

            # Generate embeddings for test content
            embeddings = await self.embedding_service.generate_embeddings(test_texts)

            # Create payloads with metadata
            payloads = []
            for i, text in enumerate(test_texts):
                payload = {
                    "content": text,
                    "document_id": f"test_doc_{i}",
                    "chapter": f"test_chapter_{i % 3}",  # Cycle through 3 chapters
                    "section_title": f"Test Section {i}",
                    "position": i,
                    "metadata": {"test": True, "original_text_length": len(text)}
                }
                payloads.append(payload)

            # Generate IDs for the test vectors
            ids = [f"test_id_{i}" for i in range(num_vectors)]

            # Add vectors to Qdrant
            success = self.qdrant_service.add_vectors(embeddings, payloads, ids)

            if success:
                logger.info(f"Added {num_vectors} test vectors to collection")
            else:
                logger.error("Failed to add test vectors to collection")

            return success

        except Exception as e:
            logger.error(f"Error adding test vectors: {e}")
            return False

    async def test_basic_search(self, query_text: str = "artificial intelligence in robotics") -> List[Dict[str, Any]]:
        """
        Test basic vector search functionality.

        Args:
            query_text: Text to search for

        Returns:
            List of search results
        """
        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(query_text)

            # Perform search
            results = self.qdrant_service.search_vectors(
                query_vector=query_embedding,
                top_k=5
            )

            logger.info(f"Basic search for '{query_text}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error performing basic search: {e}")
            return []

    async def test_search_with_filters(self) -> List[Dict[str, Any]]:
        """
        Test vector search with filters.

        Returns:
            List of search results
        """
        try:
            # Generate a query embedding
            query_text = "mechanical engineering in robotics"
            query_embedding = await self.embedding_service.generate_embedding(query_text)

            # Perform search with filters
            results = self.qdrant_service.search_vectors(
                query_vector=query_embedding,
                top_k=5,
                filters={"chapter": "test_chapter_1"}  # Filter by a specific chapter
            )

            logger.info(f"Filtered search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error performing filtered search: {e}")
            return []

    async def test_nearest_neighbor_search(self) -> Dict[str, Any]:
        """
        Test nearest-neighbor search functionality.

        Returns:
            Dictionary with test results
        """
        try:
            # First, get a vector from the collection to use as a reference
            all_chunks = self.qdrant_service.get_chunks_by_document("test_doc_0")
            if not all_chunks:
                # If we don't have chunks with this ID, try to get any point
                all_points = self.qdrant_service.get_collection_info()
                if all_points.get('point_count', 0) > 0:
                    # Get a random point as reference
                    reference_result = self.qdrant_service.get_chunk_by_id("test_id_0")
                    if reference_result:
                        reference_vector = reference_result.get('payload', {}).get('content', 'robotics')
                        query_embedding = await self.embedding_service.generate_embedding(reference_vector)
                    else:
                        # Use a default query if we can't get a reference
                        query_embedding = await self.embedding_service.generate_embedding("robotics")
                else:
                    # Use a default query if the collection is empty
                    query_embedding = await self.embedding_service.generate_embedding("artificial intelligence")
            else:
                query_embedding = await self.embedding_service.generate_embedding(
                    all_chunks[0].get('payload', {}).get('content', 'robotics')
                )

            # Perform nearest neighbor search
            results = self.qdrant_service.search_vectors(
                query_vector=query_embedding,
                top_k=3
            )

            logger.info(f"Nearest neighbor search returned {len(results)} results")

            return {
                "success": True,
                "result_count": len(results),
                "results": results,
                "query_embedding_length": len(query_embedding) if query_embedding else 0
            }

        except Exception as e:
            logger.error(f"Error performing nearest neighbor search: {e}")
            return {
                "success": False,
                "error": str(e),
                "result_count": 0,
                "results": [],
                "query_embedding_length": 0
            }

    async def test_performance(self) -> Dict[str, Any]:
        """
        Test search performance with timing measurements.

        Returns:
            Dictionary with performance metrics
        """
        try:
            # Generate multiple query embeddings
            queries = [
                "artificial intelligence",
                "machine learning in robotics",
                "computer vision applications",
                "robotics engineering",
                "neural networks"
            ]

            total_time = 0
            all_results = []

            for query in queries:
                start_time = time.time()

                # Generate embedding and search
                query_embedding = await self.embedding_service.generate_embedding(query)
                results = self.qdrant_service.search_vectors(
                    query_vector=query_embedding,
                    top_k=3
                )

                query_time = time.time() - start_time
                total_time += query_time
                all_results.extend(results)

                logger.debug(f"Query '{query}' took {query_time:.3f}s and returned {len(results)} results")

            avg_time = total_time / len(queries) if queries else 0
            total_results = len(all_results)

            performance_metrics = {
                "total_queries": len(queries),
                "total_results": total_results,
                "total_time_seconds": total_time,
                "average_time_per_query": avg_time,
                "queries_per_second": 1 / avg_time if avg_time > 0 else 0,
                "status": "success" if avg_time < 1.0 else "slow"  # Flag if queries take more than 1 second
            }

            logger.info(f"Performance test: avg {avg_time:.3f}s per query, {total_results} total results")
            return performance_metrics

        except Exception as e:
            logger.error(f"Error performing performance test: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def test_similarity_scoring(self) -> Dict[str, Any]:
        """
        Test that similarity scores are being returned properly.

        Returns:
            Dictionary with similarity scoring results
        """
        try:
            # Perform a search
            query_text = "robotics applications"
            query_embedding = await self.embedding_service.generate_embedding(query_text)

            results = self.qdrant_service.search_vectors(
                query_vector=query_embedding,
                top_k=5
            )

            # Analyze similarity scores
            scores = [result.get('score', 0) for result in results]
            avg_score = sum(scores) / len(scores) if scores else 0
            min_score = min(scores) if scores else 0
            max_score = max(scores) if scores else 0

            scoring_results = {
                "total_results": len(results),
                "scores": scores,
                "average_score": avg_score,
                "min_score": min_score,
                "max_score": max_score,
                "scores_valid": all(s >= 0 and s <= 1 for s in scores)  # Cosine similarity should be between -1 and 1, but typically 0-1 for our use case
            }

            logger.info(f"Similarity scoring test: avg={avg_score:.3f}, range=[{min_score:.3f}, {max_score:.3f}]")
            return scoring_results

        except Exception as e:
            logger.error(f"Error performing similarity scoring test: {e}")
            return {
                "total_results": 0,
                "scores": [],
                "average_score": 0,
                "min_score": 0,
                "max_score": 0,
                "scores_valid": False,
                "error": str(e)
            }

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """
        Run all vector search tests and return comprehensive results.

        Returns:
            Dictionary with comprehensive test results
        """
        logger.info("Starting comprehensive vector search tests...")

        # Create test collection
        collection_created = await self.create_test_collection()
        if not collection_created:
            logger.error("Failed to create test collection, aborting tests")
            return {"status": "error", "error": "Failed to create test collection"}

        # Add test vectors
        vectors_added = await self.add_test_vectors(10)
        if not vectors_added:
            logger.error("Failed to add test vectors, aborting tests")
            return {"status": "error", "error": "Failed to add test vectors"}

        # Run individual tests
        basic_search_results = await self.test_basic_search()
        filtered_search_results = await self.test_search_with_filters()
        nearest_neighbor_results = await self.test_nearest_neighbor_search()
        performance_results = await self.test_performance()
        similarity_results = await self.test_similarity_scoring()

        # Compile comprehensive results
        comprehensive_results = {
            "status": "completed",
            "timestamp": time.time(),
            "tests": {
                "basic_search": {
                    "result_count": len(basic_search_results),
                    "success": len(basic_search_results) > 0
                },
                "filtered_search": {
                    "result_count": len(filtered_search_results),
                    "success": len(filtered_search_results) > 0
                },
                "nearest_neighbor": nearest_neighbor_results,
                "performance": performance_results,
                "similarity_scoring": similarity_results
            },
            "summary": {
                "total_tests": 5,
                "successful_tests": sum([
                    len(basic_search_results) > 0,
                    len(filtered_search_results) > 0,
                    nearest_neighbor_results.get("success", False),
                    performance_results.get("status") == "success",
                    similarity_results.get("scores_valid", False)
                ])
            }
        }

        logger.info(f"Comprehensive tests completed. Successful: {comprehensive_results['summary']['successful_tests']}/5")
        return comprehensive_results

    async def cleanup_test_collection(self, collection_name: str = "test_textbook_content") -> bool:
        """
        Clean up the test collection.

        Args:
            collection_name: Name of the test collection to delete

        Returns:
            True if collection was deleted successfully, False otherwise
        """
        try:
            success = self.qdrant_service.delete_collection()
            if success:
                logger.info(f"Test collection '{collection_name}' deleted successfully")
            else:
                logger.warning(f"Failed to delete test collection '{collection_name}'")

            return success
        except Exception as e:
            logger.error(f"Error deleting test collection: {e}")
            return False


async def main():
    """Main function to run vector search tests."""
    logger.info("Starting vector search and nearest-neighbor query tests...")

    tester = VectorSearchTester()

    try:
        # Run comprehensive tests
        results = await tester.run_comprehensive_tests()
        print("Comprehensive Test Results:")
        print(f"Status: {results['status']}")
        print(f"Successful tests: {results['summary']['successful_tests']}/5")
        print(f"Tests: {results['tests']}")

        # Run a specific test to demonstrate functionality
        print("\nRunning a specific search test...")
        specific_results = await tester.test_basic_search("artificial intelligence in robotics")
        print(f"Search returned {len(specific_results)} results:")
        for i, result in enumerate(specific_results[:3]):  # Show first 3 results
            print(f"  {i+1}. Score: {result.get('score', 0):.3f}, Content: {result.get('payload', {}).get('content', '')[:100]}...")

    except Exception as e:
        logger.error(f"Error running tests: {e}")
    finally:
        # Clean up test collection
        await tester.cleanup_test_collection()
        print("\nTest cleanup completed.")


if __name__ == "__main__":
    asyncio.run(main())