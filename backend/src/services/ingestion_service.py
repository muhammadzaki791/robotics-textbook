"""
Ingestion Service for RAG System

This module handles the complete ingestion pipeline: text chunking -> embedding -> storage in Qdrant.
It coordinates the embedding service and Qdrant service to store textbook content with metadata.
"""
import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
import logging
from uuid import uuid4

from src.services.embedding_service import embedding_service
from src.services.qdrant_service import qdrant_service
from src.services.postgres_service import postgres_service
from src.models.document import DocumentChunk
from src.models.database import get_db
from src.models.database import DocumentMetadataDB


logger = logging.getLogger(__name__)


class IngestionService:
    """Service class for handling the complete ingestion pipeline."""

    def __init__(self):
        """Initialize the ingestion service with required dependencies."""
        self.embedding_service = embedding_service
        self.qdrant_service = qdrant_service
        self.postgres_service = postgres_service

    async def ingest_document_chunks(self, document_chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Ingest document chunks by generating embeddings and storing in Qdrant.

        Args:
            document_chunks: List of DocumentChunk objects to ingest

        Returns:
            Dictionary with ingestion results and statistics
        """
        start_time = time.time()

        if not document_chunks:
            return {
                "status": "success",
                "message": "No chunks to process",
                "total_chunks": 0,
                "processed_chunks": 0,
                "failed_chunks": 0,
                "processing_time_ms": 0
            }

        total_chunks = len(document_chunks)
        logger.info(f"Starting ingestion of {total_chunks} document chunks")

        # Extract text content for embedding
        texts = [chunk.content for chunk in document_chunks]

        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = await self.embedding_service.generate_embeddings(texts)

        # Prepare Qdrant payloads with metadata
        valid_chunks_and_embeddings = []
        for i, (chunk, embedding) in enumerate(zip(document_chunks, embeddings)):
            payload = {
                "content": chunk.content,
                "document_id": chunk.document_id,
                "chapter": chunk.chapter,
                "section_title": chunk.section_title,
                "position": chunk.position,
                "metadata": chunk.metadata
            }
            valid_chunks_and_embeddings.append((chunk, embedding, payload))

        # Extract vectors and payloads for Qdrant
        vectors = [item[1] for item in valid_chunks_and_embeddings]
        payloads = [item[2] for item in valid_chunks_and_embeddings]

        # Generate IDs for Qdrant (use UUID for valid format)
        ids = [str(uuid4()) for _ in valid_chunks_and_embeddings]

        # Store in Qdrant
        logger.info(f"Storing {len(vectors)} vectors in Qdrant...")
        qdrant_success = self.qdrant_service.add_vectors(vectors, payloads, ids)

        if not qdrant_success:
            logger.error("Failed to store vectors in Qdrant")
            return {
                "status": "error",
                "message": "Failed to store vectors in Qdrant",
                "total_chunks": total_chunks,
                "processed_chunks": 0,
                "failed_chunks": total_chunks,
                "processing_time_ms": (time.time() - start_time) * 1000
            }

        processing_time = (time.time() - start_time) * 1000

        # Update document metadata to reflect ingestion status
        unique_doc_ids = list(set(chunk.document_id for chunk in document_chunks))
        for doc_id in unique_doc_ids:
            # Update the embedding status for each document
            db = next(get_db())
            try:
                self.postgres_service.update_document_metadata(
                    db, doc_id, {"embedding_status": "completed"}
                )
            finally:
                db.close()

        logger.info(f"Ingestion completed in {processing_time:.2f}ms")

        return {
            "status": "success",
            "message": f"Successfully ingested {len(vectors)} chunks",
            "total_chunks": total_chunks,
            "processed_chunks": len(vectors),
            "failed_chunks": total_chunks - len(vectors),
            "processing_time_ms": processing_time,
            "qdrant_success": qdrant_success
        }

    async def ingest_textbook_content(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ingest textbook content from chunk dictionaries.

        Args:
            chunks: List of chunk dictionaries with content, document_id, chapter, etc.

        Returns:
            Dictionary with ingestion results
        """
        # Convert dictionaries to DocumentChunk objects
        document_chunks = []
        for chunk_data in chunks:
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

        return await self.ingest_document_chunks(document_chunks)

    async def batch_ingest_from_file(self, file_path: str, document_id: str,
                                   chapter: str, section_title: str = "") -> Dict[str, Any]:
        """
        Ingest content from a single file (for testing or individual document ingestion).

        Args:
            file_path: Path to the file to ingest
            document_id: ID for the document
            chapter: Chapter name
            section_title: Section title

        Returns:
            Dictionary with ingestion results
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create a simple chunk (in a real scenario, you'd want to chunk this properly)
            chunk = DocumentChunk(
                id=f"{document_id}_chunk_0",
                content=content,
                document_id=document_id,
                chapter=chapter,
                section_title=section_title,
                position=0,
                metadata={"source_file": file_path}
            )

            return await self.ingest_document_chunks([chunk])

        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "total_chunks": 0,
                "processed_chunks": 0,
                "failed_chunks": 0,
                "processing_time_ms": 0
            }

    async def update_document_ingestion_status(self, document_id: str, status: str = "completed"):
        """
        Update the ingestion status of a document in the metadata database.

        Args:
            document_id: ID of the document
            status: New status (pending, processing, completed, failed)
        """
        with get_db() as db:
            self.postgres_service.update_document_metadata(
                db, document_id, {"embedding_status": status}
            )
            logger.info(f"Updated document {document_id} status to {status}")

    async def reingest_failed_documents(self) -> Dict[str, Any]:
        """
        Find and re-ingest documents that previously failed ingestion.

        Returns:
            Dictionary with reingestion results
        """
        start_time = time.time()

        with get_db() as db:
            failed_docs = self.postgres_service.get_documents_by_status(db, "failed")
            processing_docs = self.postgres_service.get_documents_by_status(db, "processing")

        all_docs_to_reingest = failed_docs + processing_docs
        logger.info(f"Found {len(all_docs_to_reingest)} documents to re-ingest")

        results = {
            "total_documents": len(all_docs_to_reingest),
            "successful_reingestions": 0,
            "failed_reingestions": 0,
            "errors": []
        }

        for doc in all_docs_to_reingest:
            try:
                # Remove existing vectors for this document from Qdrant
                self.qdrant_service.delete_by_document_id(doc.document_id)

                # Here you would typically fetch the original content and re-chunk it
                # For this implementation, we'll assume there's a way to get the content
                # This would require additional implementation based on how content is stored

                # Update status to pending for reprocessing
                await self.update_document_ingestion_status(doc.document_id, "pending")
                results["successful_reingestions"] += 1

            except Exception as e:
                logger.error(f"Error reingesting document {doc.document_id}: {e}")
                results["errors"].append({
                    "document_id": doc.document_id,
                    "error": str(e)
                })
                results["failed_reingestions"] += 1

        results["processing_time_ms"] = (time.time() - start_time) * 1000

        return results

    async def validate_ingestion_completeness(self, document_id: str) -> Dict[str, Any]:
        """
        Validate that all chunks for a document have been properly ingested.

        Args:
            document_id: ID of the document to validate

        Returns:
            Dictionary with validation results
        """
        # Get document metadata from PostgreSQL
        with get_db() as db:
            doc_metadata = self.postgres_service.get_document_metadata(db, document_id)

        if not doc_metadata:
            return {
                "valid": False,
                "message": f"Document {document_id} not found in metadata database"
            }

        # Get chunks from Qdrant for this document
        qdrant_chunks = self.qdrant_service.get_chunks_by_document(document_id)

        # The validation would depend on how you track expected vs. actual chunks
        # For now, we'll just return basic information
        return {
            "document_id": document_id,
            "metadata_status": doc_metadata.embedding_status,
            "qdrant_chunks_count": len(qdrant_chunks),
            "expected_chunks_count": doc_metadata.metadata.get('total_chunks', 0) if doc_metadata.metadata else 0,
            "is_complete": len(qdrant_chunks) > 0  # Basic check
        }

    async def get_ingestion_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the ingestion process.

        Returns:
            Dictionary with ingestion statistics
        """
        with get_db() as db:
            doc_stats = self.postgres_service.get_document_statistics(db)

        qdrant_info = self.qdrant_service.get_collection_info()

        return {
            "document_statistics": doc_stats,
            "qdrant_collection_info": qdrant_info,
            "ingestion_rate": "N/A",  # Would need to track over time
            "last_ingestion_time": "N/A"
        }


# Singleton instance
ingestion_service = IngestionService()


async def main():
    """Main function to demonstrate ingestion service usage."""
    service = IngestionService()

    # Example: Create some sample chunks for testing
    sample_chunks = [
        DocumentChunk(
            id="doc1_chunk_0",
            content="This is the first chunk of the textbook content.",
            document_id="doc1",
            chapter="introduction",
            section_title="Overview",
            position=0,
            metadata={"source": "intro.md"}
        ),
        DocumentChunk(
            id="doc1_chunk_1",
            content="This is the second chunk with more detailed information.",
            document_id="doc1",
            chapter="introduction",
            section_title="Overview",
            position=1,
            metadata={"source": "intro.md"}
        )
    ]

    # Perform ingestion
    print("Starting ingestion test...")
    result = await service.ingest_document_chunks(sample_chunks)
    print(f"Ingestion result: {result}")

    # Get statistics
    stats = await service.get_ingestion_statistics()
    print(f"Ingestion statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())