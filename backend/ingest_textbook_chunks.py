#!/usr/bin/env python3
"""
Ingest Textbook Chunks into RAG System

This script loads the chunked textbook content from JSON and ingests it into the Qdrant vector database.
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the src directory to the path so we can import our services
sys.path.insert(0, str(Path(__file__).parent))

from src.services.ingestion_service import ingestion_service
from src.models.document import DocumentChunk
from uuid import uuid4


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
    """Main function to ingest textbook chunks into the RAG system."""
    print("Starting textbook content ingestion process...")

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

        # Perform ingestion
        print("Starting ingestion into vector database...")
        result = await ingestion_service.ingest_document_chunks(document_chunks)

        print(f"Ingestion completed with result: {result}")

        if result['status'] == 'success':
            print(f"Successfully ingested {result['processed_chunks']} chunks")
            if result['failed_chunks'] > 0:
                print(f"Warning: {result['failed_chunks']} chunks failed to ingest")

            print(f"Processing time: {result['processing_time_ms']:.2f}ms")
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