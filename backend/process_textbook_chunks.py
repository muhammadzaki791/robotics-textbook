"""
Textbook Content Chunking Script

This script processes the entire textbook content using the chunking strategy
and prepares it for embedding and storage in the RAG system.
"""
import json
import os
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

from src.utils.chunking import ChunkingStrategy, DocumentChunk
from src.utils.content_exporter import ContentExporter


def load_textbook_content(textbook_dir: str) -> List[Dict[str, str]]:
    """
    Load all textbook content from the specified directory.

    Args:
        textbook_dir: Path to the textbook directory

    Returns:
        List of dictionaries containing file information and content
    """
    exporter = ContentExporter(textbook_dir)
    return exporter.export_all_content()


def chunk_textbook_content(textbook_dir: str, chunk_size: int = 512, overlap_size: int = 51) -> List[DocumentChunk]:
    """
    Process entire textbook content and create chunks.

    Args:
        textbook_dir: Path to the textbook directory
        chunk_size: Target size of each chunk in tokens
        overlap_size: Number of overlapping tokens between chunks

    Returns:
        List of DocumentChunk objects
    """
    print(f"Loading textbook content from: {textbook_dir}")

    # Load all textbook content
    content_list = load_textbook_content(textbook_dir)
    print(f"Loaded {len(content_list)} textbook files")

    # Initialize chunking strategy
    chunker = ChunkingStrategy(chunk_size=chunk_size, overlap_size=overlap_size)

    all_chunks = []
    processed_files = 0

    print("Processing content and creating chunks...")

    for content_item in tqdm(content_list, desc="Processing files"):
        try:
            # Extract content information
            file_path = content_item['file_path']
            content = content_item['content']
            document_id = content_item['document_id']
            chapter = content_item.get('chapter', 'unknown')
            title = content_item.get('title', 'unknown')

            # Chunk the content
            chunks = chunker.chunk_text(content, document_id, chapter, title)

            # Add source file information to metadata
            for chunk in chunks:
                chunk.metadata['source_file'] = file_path
                chunk.metadata['relative_path'] = content_item.get('relative_path', '')
                chunk.metadata['title'] = title
                chunk.metadata['chapter'] = chapter

            all_chunks.extend(chunks)
            processed_files += 1

        except Exception as e:
            print(f"Error processing {content_item.get('file_path', 'unknown')}: {e}")
            continue

    print(f"Successfully processed {processed_files} files")
    print(f"Created {len(all_chunks)} total chunks")

    return all_chunks


def save_chunks_to_json(chunks: List[DocumentChunk], output_file: str):
    """
    Save chunks to a JSON file.

    Args:
        chunks: List of DocumentChunk objects
        output_file: Output file path
    """
    print(f"Saving {len(chunks)} chunks to {output_file}")

    # Convert DocumentChunk objects to dictionaries
    chunk_dicts = []
    for chunk in chunks:
        chunk_dict = {
            'id': chunk.id,
            'content': chunk.content,
            'document_id': chunk.document_id,
            'chapter': chunk.chapter,
            'section_title': chunk.section_title,
            'position': chunk.position,
            'token_count': chunk.token_count,
            'metadata': chunk.metadata
        }
        chunk_dicts.append(chunk_dict)

    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_dicts, f, indent=2, ensure_ascii=False)

    print(f"Successfully saved chunks to {output_file}")


def save_chunks_to_txt(chunks: List[DocumentChunk], output_dir: str):
    """
    Save chunks to individual text files organized by document.

    Args:
        chunks: List of DocumentChunk objects
        output_dir: Output directory
    """
    print(f"Saving chunks to individual files in {output_dir}")

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Group chunks by document
    chunks_by_document = {}
    for chunk in chunks:
        if chunk.document_id not in chunks_by_document:
            chunks_by_document[chunk.document_id] = []
        chunks_by_document[chunk.document_id].append(chunk)

    # Save chunks for each document
    for doc_id, doc_chunks in chunks_by_document.items():
        # Create subdirectory for each document
        doc_dir = Path(output_dir) / doc_id
        doc_dir.mkdir(exist_ok=True)

        for chunk in doc_chunks:
            chunk_file = doc_dir / f"chunk_{chunk.position:04d}.txt"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk.content)

    print(f"Successfully saved chunks to {output_dir}")


def validate_chunk_quality(chunks: List[DocumentChunk], chunker: ChunkingStrategy) -> Dict[str, any]:
    """
    Validate the quality of all chunks.

    Args:
        chunks: List of DocumentChunk objects
        chunker: ChunkingStrategy instance for validation

    Returns:
        Dictionary with validation metrics
    """
    print("Validating chunk quality...")

    # Use the chunker's validation method
    validation = chunker.validate_chunk_quality(chunks)

    # Additional validations specific to textbook content
    validation['total_documents'] = len(set(chunk.document_id for chunk in chunks))
    validation['avg_chunks_per_document'] = validation['total_chunks'] / validation['total_documents'] if validation['total_documents'] > 0 else 0

    # Check for very small chunks (might indicate poor chunking)
    tiny_chunks = sum(1 for chunk in chunks if chunk.token_count < 50)
    validation['tiny_chunks'] = tiny_chunks
    validation['tiny_chunks_percentage'] = (tiny_chunks / validation['total_chunks']) * 100 if validation['total_chunks'] > 0 else 0

    # Check for very large chunks (might exceed limits)
    large_chunks = sum(1 for chunk in chunks if chunk.token_count > chunker.chunk_size + chunker.overlap_size)
    validation['large_chunks'] = large_chunks

    return validation


def main():
    """Main function to process textbook content and create chunks."""
    # Set the textbook directory path
    textbook_dir = "C:/Users/dell/OneDrive/Desktop/Zaki-Projects/Q4/New folder/Book/docs/robotics-textbook"

    # Set chunking parameters
    chunk_size = 512  # 512-token chunks
    overlap_size = 51  # 10% overlap

    print(f"Starting textbook chunking process...")
    print(f"Textbook directory: {textbook_dir}")
    print(f"Chunk size: {chunk_size} tokens")
    print(f"Overlap size: {overlap_size} tokens")

    # Process the textbook content
    all_chunks = chunk_textbook_content(textbook_dir, chunk_size, overlap_size)

    # Initialize chunker for validation
    chunker = ChunkingStrategy(chunk_size=chunk_size, overlap_size=overlap_size)

    # Validate chunk quality
    validation = validate_chunk_quality(all_chunks, chunker)

    print("\nChunk Quality Report:")
    print(f"Total documents processed: {validation['total_documents']}")
    print(f"Total chunks created: {validation['total_chunks']}")
    print(f"Average chunks per document: {validation['avg_chunks_per_document']:.2f}")
    print(f"Average tokens per chunk: {validation['avg_token_count']:.2f}")
    print(f"Max tokens in a chunk: {validation['max_token_count']}")
    print(f"Min tokens in a chunk: {validation['min_token_count']}")
    print(f"Total tokens: {validation['total_tokens']}")
    print(f"Tiny chunks (<50 tokens): {validation['tiny_chunks']} ({validation['tiny_chunks_percentage']:.2f}%)")
    print(f"Large chunks (exceeding limit): {validation['large_chunks']}")

    # Save chunks to JSON file
    save_chunks_to_json(all_chunks, "textbook_chunks.json")

    # Optionally save to individual text files as well
    save_chunks_to_txt(all_chunks, "chunked_textbook_content")

    # Create a summary report
    report = {
        'summary': {
            'total_documents': validation['total_documents'],
            'total_chunks': validation['total_chunks'],
            'avg_chunks_per_document': validation['avg_chunks_per_document'],
            'total_tokens': validation['total_tokens'],
            'chunk_size': chunk_size,
            'overlap_size': overlap_size
        },
        'validation': validation
    }

    with open("chunking_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nChunking process completed successfully!")
    print(f"Output files:")
    print(f"  - textbook_chunks.json: All chunks in JSON format")
    print(f"  - chunked_textbook_content/: Individual chunk files organized by document")
    print(f"  - chunking_report.json: Quality validation report")


if __name__ == "__main__":
    main()