"""
Document Metadata Service for RAG System

This module handles the creation and management of document metadata records
in the Neon Postgres database for the RAG system.
"""
import asyncio
import hashlib
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from src.models.database import get_db, DocumentMetadataDB
from src.services.postgres_service import postgres_service
from src.models.document import DocumentMetadata
from src.utils.content_exporter import ContentExporter


logger = logging.getLogger(__name__)


class DocumentMetadataService:
    """Service class for managing document metadata in the database."""

    def __init__(self):
        """Initialize the document metadata service."""
        self.postgres_service = postgres_service

    def calculate_content_checksum(self, content: str) -> str:
        """
        Calculate SHA-256 checksum for content to detect changes.

        Args:
            content: Content string to calculate checksum for

        Returns:
            SHA-256 checksum as hex string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def create_document_metadata_record(self, doc_metadata: DocumentMetadata) -> Optional[DocumentMetadataDB]:
        """
        Create a single document metadata record in the database.

        Args:
            doc_metadata: DocumentMetadata object with the data

        Returns:
            Created DocumentMetadataDB object if successful, None otherwise
        """
        with get_db() as db:
            try:
                created_record = self.postgres_service.create_document_metadata(db, doc_metadata)
                logger.info(f"Created document metadata record for {doc_metadata.document_id}")
                return created_record
            except Exception as e:
                logger.error(f"Error creating document metadata record: {e}")
                return None

    def create_multiple_document_metadata_records(self, doc_metadata_list: List[DocumentMetadata]) -> Dict[str, Any]:
        """
        Create multiple document metadata records in the database.

        Args:
            doc_metadata_list: List of DocumentMetadata objects

        Returns:
            Dictionary with creation results
        """
        created_count = 0
        failed_count = 0
        failed_documents = []
        created_documents = []

        for doc_metadata in doc_metadata_list:
            result = self.create_document_metadata_record(doc_metadata)
            if result:
                created_count += 1
                created_documents.append(result.document_id)
            else:
                failed_count += 1
                failed_documents.append(doc_metadata.document_id)

        return {
            "total_documents": len(doc_metadata_list),
            "created_count": created_count,
            "failed_count": failed_count,
            "created_documents": created_documents,
            "failed_documents": failed_documents,
            "success_rate": created_count / len(doc_metadata_list) if doc_metadata_list else 0
        }

    def update_document_metadata_record(self, document_id: str, updates: Dict[str, Any]) -> Optional[DocumentMetadataDB]:
        """
        Update an existing document metadata record.

        Args:
            document_id: ID of the document to update
            updates: Dictionary of fields to update

        Returns:
            Updated DocumentMetadataDB object if successful, None otherwise
        """
        with get_db() as db:
            try:
                updated_record = self.postgres_service.update_document_metadata(db, document_id, updates)
                if updated_record:
                    logger.info(f"Updated document metadata record for {document_id}")
                else:
                    logger.warning(f"Document metadata record not found for {document_id}")
                return updated_record
            except Exception as e:
                logger.error(f"Error updating document metadata record for {document_id}: {e}")
                return None

    def get_document_metadata_record(self, document_id: str) -> Optional[DocumentMetadataDB]:
        """
        Get a document metadata record by document ID.

        Args:
            document_id: ID of the document

        Returns:
            DocumentMetadataDB object if found, None otherwise
        """
        with get_db() as db:
            try:
                record = self.postgres_service.get_document_metadata(db, document_id)
                return record
            except Exception as e:
                logger.error(f"Error getting document metadata record for {document_id}: {e}")
                return None

    def create_or_update_document_metadata(self, doc_metadata: DocumentMetadata) -> Optional[DocumentMetadataDB]:
        """
        Create a document metadata record if it doesn't exist, or update it if it does.

        Args:
            doc_metadata: DocumentMetadata object with the data

        Returns:
            Created/Updated DocumentMetadataDB object if successful, None otherwise
        """
        existing_record = self.get_document_metadata_record(doc_metadata.document_id)

        if existing_record:
            # Update existing record
            updates = {
                "title": doc_metadata.title,
                "chapter": doc_metadata.chapter,
                "section": doc_metadata.section,
                "page_reference": doc_metadata.page_reference,
                "url_path": doc_metadata.url_path,
                "word_count": doc_metadata.word_count,
                "embedding_status": doc_metadata.embedding_status,
                "checksum": doc_metadata.checksum,
                "metadata": doc_metadata.metadata,
                "updated_at": datetime.utcnow()
            }
            return self.update_document_metadata_record(doc_metadata.document_id, updates)
        else:
            # Create new record
            return self.create_document_metadata_record(doc_metadata)

    def create_document_metadata_from_file(self, file_path: str, document_id: Optional[str] = None,
                                         chapter: Optional[str] = None, section: Optional[str] = None) -> Optional[DocumentMetadataDB]:
        """
        Create document metadata record from a file.

        Args:
            file_path: Path to the file
            document_id: Optional document ID (will be generated from file path if not provided)
            chapter: Optional chapter name
            section: Optional section name

        Returns:
            Created DocumentMetadataDB object if successful, None otherwise
        """
        try:
            # Read the file to get content and calculate word count
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Calculate checksum
            checksum = self.calculate_content_checksum(content)

            # Calculate word count
            word_count = len(content.split())

            # Generate document ID if not provided
            if not document_id:
                import os
                # Use the relative path with separators replaced by underscores
                relative_path = os.path.relpath(file_path).replace(os.sep, '_').replace('.md', '')
                document_id = relative_path

            # Extract title from content (first heading) or filename
            title = self._extract_title_from_content(content) or os.path.basename(file_path)

            # Create DocumentMetadata object
            doc_metadata = DocumentMetadata(
                document_id=document_id,
                title=title,
                chapter=chapter or "unknown",
                section=section or "",
                page_reference=None,
                url_path=file_path.replace("\\", "/").replace("docs/", "/"),  # Convert to URL path
                word_count=word_count,
                embedding_status="pending",  # New documents start with pending status
                checksum=checksum,
                metadata={"source_file": file_path, "created_at": datetime.utcnow().isoformat()}
            )

            return self.create_document_metadata_record(doc_metadata)

        except Exception as e:
            logger.error(f"Error creating document metadata from file {file_path}: {e}")
            return None

    def _extract_title_from_content(self, content: str) -> Optional[str]:
        """
        Extract title from content (first heading).

        Args:
            content: Content string

        Returns:
            Extracted title or None if not found
        """
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()  # Remove '# ' prefix
            elif line.startswith('#'):
                # Handle other heading levels if no level 1 heading found
                continue

        return None

    def create_metadata_from_textbook_directory(self, textbook_dir: str) -> Dict[str, Any]:
        """
        Create document metadata records for all files in a textbook directory.

        Args:
            textbook_dir: Path to the textbook directory

        Returns:
            Dictionary with creation results
        """
        # Use the ContentExporter to find all files
        exporter = ContentExporter(textbook_dir)
        content_list = exporter.export_all_content()

        created_count = 0
        failed_count = 0
        failed_files = []
        created_files = []

        for content_item in content_list:
            try:
                # Create DocumentMetadata object from content item
                doc_metadata = DocumentMetadata(
                    document_id=content_item['document_id'],
                    title=content_item['title'],
                    chapter=content_item['chapter'],
                    section="",
                    page_reference=None,
                    url_path=content_item['relative_path'].replace('.md', '').replace('\\', '/'),
                    word_count=len(content_item['content'].split()),
                    embedding_status="pending",
                    checksum=self.calculate_content_checksum(content_item['content']),
                    metadata={
                        "source_file": content_item['file_path'],
                        "relative_path": content_item['relative_path'],
                        "created_at": datetime.utcnow().isoformat()
                    }
                )

                result = self.create_document_metadata_record(doc_metadata)
                if result:
                    created_count += 1
                    created_files.append(content_item['file_path'])
                else:
                    failed_count += 1
                    failed_files.append(content_item['file_path'])

            except Exception as e:
                logger.error(f"Error processing file {content_item['file_path']}: {e}")
                failed_count += 1
                failed_files.append(content_item['file_path'])

        return {
            "total_files": len(content_list),
            "created_count": created_count,
            "failed_count": failed_count,
            "created_files": created_files,
            "failed_files": failed_files,
            "success_rate": created_count / len(content_list) if content_list else 0
        }

    def check_content_changes(self, document_id: str, new_content: str) -> bool:
        """
        Check if content has changed by comparing checksums.

        Args:
            document_id: ID of the document
            new_content: New content to compare

        Returns:
            True if content has changed, False otherwise
        """
        existing_record = self.get_document_metadata_record(document_id)

        if not existing_record:
            return True  # Document doesn't exist, so it's new

        new_checksum = self.calculate_content_checksum(new_content)
        return existing_record.checksum != new_checksum

    def update_document_status(self, document_id: str, status: str) -> bool:
        """
        Update the embedding status of a document.

        Args:
            document_id: ID of the document
            status: New status (pending, processing, completed, failed)

        Returns:
            True if update was successful, False otherwise
        """
        result = self.update_document_metadata_record(document_id, {"embedding_status": status})
        return result is not None

    def get_documents_by_status(self, status: str) -> List[DocumentMetadataDB]:
        """
        Get all documents with a specific embedding status.

        Args:
            status: Status to filter by

        Returns:
            List of DocumentMetadataDB objects with the specified status
        """
        with get_db() as db:
            try:
                return self.postgres_service.get_documents_by_status(db, status)
            except Exception as e:
                logger.error(f"Error getting documents by status {status}: {e}")
                return []

    def get_all_documents(self) -> List[DocumentMetadataDB]:
        """
        Get all document metadata records.

        Returns:
            List of all DocumentMetadataDB objects
        """
        with get_db() as db:
            try:
                return self.postgres_service.get_all_documents(db)
            except Exception as e:
                logger.error(f"Error getting all documents: {e}")
                return []


# Singleton instance
document_metadata_service = DocumentMetadataService()


async def main():
    """Main function to demonstrate document metadata service usage."""
    service = DocumentMetadataService()

    # Example: Create a sample document metadata record
    sample_metadata = DocumentMetadata(
        document_id="sample_doc_001",
        title="Sample Document",
        chapter="introduction",
        section="overview",
        page_reference="1-10",
        url_path="/introduction/overview",
        word_count=500,
        embedding_status="pending",
        checksum="abc123",
        metadata={"author": "test", "version": "1.0"}
    )

    print("Creating sample document metadata...")
    result = service.create_document_metadata_record(sample_metadata)
    print(f"Creation result: {result is not None}")

    # Example: Create multiple records
    sample_records = [
        DocumentMetadata(
            document_id="sample_doc_002",
            title="Sample Document 2",
            chapter="chapter2",
            section="section1",
            page_reference="15-20",
            url_path="/chapter2/section1",
            word_count=300,
            embedding_status="pending",
            checksum="def456",
            metadata={"author": "test", "version": "1.0"}
        ),
        DocumentMetadata(
            document_id="sample_doc_003",
            title="Sample Document 3",
            chapter="chapter2",
            section="section2",
            page_reference="21-25",
            url_path="/chapter2/section2",
            word_count=400,
            embedding_status="pending",
            checksum="ghi789",
            metadata={"author": "test", "version": "1.0"}
        )
    ]

    print("Creating multiple document metadata records...")
    batch_result = service.create_multiple_document_metadata_records(sample_records)
    print(f"Batch creation result: {batch_result}")

    # Example: Get a record
    print("Getting sample document metadata...")
    retrieved = service.get_document_metadata_record("sample_doc_001")
    print(f"Retrieved: {retrieved is not None}")


if __name__ == "__main__":
    asyncio.run(main())