#!/usr/bin/env python3
"""
Batched Ingestion Script for Textbook Chunks with Rate Limiting

This script loads the chunked textbook content from JSON and ingests it into the
Qdrant vector database with proper rate limiting to avoid API errors.
"""
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from uuid import uuid4

# Add the src directory to the path so we can import our services
sys.path.insert(0, str(Path(__file__).parent))

from src.services.ingestion_service import ingestion_service
from src.models.document import DocumentChunk


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


async def ingest_in_batches(document_chunks: List[DocumentChunk], batch_size: int = 5):
    """
    Ingest document chunks in batches to respect API rate limits.

    Args:
        document_chunks: List of DocumentChunk objects to ingest
        batch_size: Number of chunks to process in each batch
    """
    total_chunks = len(document_chunks)
    print(f"Starting ingestion of {total_chunks} chunks in batches of {batch_size}...")

    successful_batches = 0
    failed_batches = 0

    for i in range(0, len(document_chunks), batch_size):
        batch = document_chunks[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(document_chunks) - 1) // batch_size + 1

        print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")

        try:
            # Process this batch
            result = await ingestion_service.ingest_document_chunks(batch)
            print(f"  Batch {batch_num} completed: {result}")
            successful_batches += 1

            # Add delay between batches to respect rate limits
            print(f"  Waiting 2 seconds before next batch...")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"  Batch {batch_num} failed: {e}")
            failed_batches += 1

            # Wait longer after a failure
            print(f"  Waiting 5 seconds before retrying or continuing...")
            await asyncio.sleep(5)

    print(f"\nIngestion completed!")
    print(f"Successful batches: {successful_batches}")
    print(f"Failed batches: {failed_batches}")
    print(f"Total chunks processed: {total_chunks}")


async def main():
    """Main function to ingest textbook chunks into the RAG system with rate limiting."""
    print("Starting batched textbook content ingestion process...")

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

        # Perform ingestion in batches
        print("Starting batched ingestion into vector database...")
        await ingest_in_batches(document_chunks, batch_size=3)  # Small batch size for API limits

        print("Textbook content is now available for RAG queries!")
        return 0

    except Exception as e:
        print(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)