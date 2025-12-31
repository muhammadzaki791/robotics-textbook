"""
Textbook Content Chunking Module

Implements chunking strategy for RAG system:
- 512-token chunks with 10% overlap (51 tokens)
- Preserve semantic boundaries
- Handle various content types appropriately
"""
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
import tiktoken


@dataclass
class DocumentChunk:
    """Represents a chunk of document content with metadata."""
    id: str
    content: str
    document_id: str
    chapter: str
    section_title: str
    position: int
    token_count: int
    metadata: Dict[str, any]


class ChunkingStrategy:
    """Implements chunking strategy for textbook content."""

    def __init__(self, chunk_size: int = 512, overlap_size: int = 51, encoding_name: str = "cl100k_base"):
        """
        Initialize chunking strategy.

        Args:
            chunk_size: Target size of each chunk in tokens
            overlap_size: Number of overlapping tokens between chunks
            encoding_name: Name of the tokenizer to use
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.encoding = tiktoken.get_encoding(encoding_name)

        # Define semantic boundaries for chunking
        self.boundary_patterns = [
            r'\n#{2,6}\s',  # Markdown headers (##, ###, etc.)
            r'\n={2,}',     # Underlined headers
            r'\n-{2,}',     # Headers with dashes
            r'\n\s*\n',     # Paragraph breaks
            r'\n\*\s',      # List items
            r'\n-\s',       # List items
            r'\n\d+\.\s',   # Numbered lists
        ]

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))

    def split_by_semantic_boundaries(self, text: str) -> List[str]:
        """
        Split text by semantic boundaries while preserving content.

        Args:
            text: Input text to split

        Returns:
            List of text segments split by semantic boundaries
        """
        # First, try to split by markdown headers
        segments = [text]

        for pattern in self.boundary_patterns:
            new_segments = []
            for segment in segments:
                # Split by the current pattern
                parts = re.split(f'({pattern})', segment)

                # Reconstruct with boundaries preserved
                temp_segments = []
                for i, part in enumerate(parts):
                    if re.match(pattern, part.strip()):
                        # This is a boundary, combine with previous segment if not empty
                        if temp_segments:
                            temp_segments[-1] += part
                        else:
                            # If it's the first part, just add it
                            temp_segments.append(part)
                    else:
                        # Regular content
                        temp_segments.append(part)

                # Combine adjacent parts to form segments
                combined_segments = []
                current_segment = ""

                for part in temp_segments:
                    if re.search('|'.join(self.boundary_patterns), part.strip()):
                        # This is a boundary
                        if current_segment.strip():
                            combined_segments.append(current_segment)
                        combined_segments.append(part)
                        current_segment = ""
                    else:
                        # Regular content
                        current_segment += part
                        if len(self.encoding.encode(current_segment)) > self.chunk_size * 2:
                            # If the current segment is getting too large,
                            # split it at sentence boundaries
                            sub_segments = self._split_large_segment(current_segment)
                            combined_segments.extend(sub_segments)
                            current_segment = ""

                if current_segment.strip():
                    combined_segments.append(current_segment)

                new_segments.extend(combined_segments)

            segments = new_segments

        # Filter out empty segments
        segments = [seg for seg in segments if seg.strip()]

        return segments

    def _split_large_segment(self, text: str) -> List[str]:
        """
        Split a large text segment into smaller parts.

        Args:
            text: Large text segment to split

        Returns:
            List of smaller text segments
        """
        # Split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        segments = []
        current_segment = ""

        for sentence in sentences:
            test_segment = current_segment + " " + sentence if current_segment else sentence

            if len(self.encoding.encode(test_segment)) <= self.chunk_size:
                current_segment = test_segment
            else:
                if current_segment:
                    segments.append(current_segment)
                current_segment = sentence

        if current_segment:
            segments.append(current_segment)

        return segments

    def chunk_text(self, text: str, document_id: str, chapter: str = "unknown",
                   section_title: str = "unknown") -> List[DocumentChunk]:
        """
        Chunk the input text according to the specified strategy.

        Args:
            text: Input text to chunk
            document_id: ID of the source document
            chapter: Chapter name
            section_title: Section title

        Returns:
            List of DocumentChunk objects
        """
        # First, split by semantic boundaries
        semantic_segments = self.split_by_semantic_boundaries(text)

        chunks = []
        chunk_id_counter = 0

        for segment in semantic_segments:
            if not segment.strip():
                continue

            segment_tokens = self.encoding.encode(segment)

            # If the segment is small enough, use it as a chunk directly
            if len(segment_tokens) <= self.chunk_size:
                chunk = DocumentChunk(
                    id=f"{document_id}_chunk_{chunk_id_counter}",
                    content=segment,
                    document_id=document_id,
                    chapter=chapter,
                    section_title=section_title,
                    position=chunk_id_counter,
                    token_count=len(segment_tokens),
                    metadata={}
                )
                chunks.append(chunk)
                chunk_id_counter += 1
            else:
                # If the segment is too large, split it further
                sub_chunks = self._chunk_large_segment(
                    segment, document_id, chapter, section_title, chunk_id_counter
                )
                chunks.extend(sub_chunks)
                chunk_id_counter += len(sub_chunks)

        # Apply overlap between consecutive chunks
        chunks_with_overlap = self._apply_overlap(chunks)

        return chunks_with_overlap

    def _chunk_large_segment(self, text: str, document_id: str, chapter: str,
                           section_title: str, start_counter: int) -> List[DocumentChunk]:
        """
        Chunk a large text segment that exceeds the token limit.

        Args:
            text: Large text segment to chunk
            document_id: ID of the source document
            chapter: Chapter name
            section_title: Section title
            start_counter: Starting counter for chunk IDs

        Returns:
            List of DocumentChunk objects
        """
        tokens = self.encoding.encode(text)
        chunks = []
        chunk_id_counter = start_counter

        start_idx = 0
        while start_idx < len(tokens):
            # Determine the end index for this chunk
            end_idx = start_idx + self.chunk_size

            # If this is not the first chunk, include overlap
            if start_idx > 0:
                overlap_start = max(0, start_idx - self.overlap_size)
                # Adjust start_idx to include overlap
                start_idx = overlap_start

            # Make sure we don't exceed the token array length
            if end_idx > len(tokens):
                end_idx = len(tokens)

            # Decode the tokens back to text
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)

            # Create chunk
            chunk = DocumentChunk(
                id=f"{document_id}_chunk_{chunk_id_counter}",
                content=chunk_text,
                document_id=document_id,
                chapter=chapter,
                section_title=section_title,
                position=chunk_id_counter,
                token_count=len(chunk_tokens),
                metadata={}
            )
            chunks.append(chunk)

            # Move to the next chunk position (excluding overlap for next iteration)
            start_idx = end_idx - self.overlap_size if end_idx < len(tokens) else len(tokens)
            chunk_id_counter += 1

        return chunks

    def _apply_overlap(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Apply overlap between consecutive chunks to maintain context.

        Args:
            chunks: List of chunks without overlap

        Returns:
            List of chunks with overlap applied
        """
        # For now, we're handling overlap during the chunking process
        # This function can be extended if needed for post-processing
        return chunks

    def validate_chunk_quality(self, chunks: List[DocumentChunk]) -> Dict[str, any]:
        """
        Validate the quality of the chunks.

        Args:
            chunks: List of DocumentChunk objects

        Returns:
            Dictionary with validation metrics
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'avg_token_count': 0,
                'max_token_count': 0,
                'min_token_count': 0,
                'total_tokens': 0
            }

        token_counts = [chunk.token_count for chunk in chunks]

        return {
            'total_chunks': len(chunks),
            'avg_token_count': sum(token_counts) / len(token_counts),
            'max_token_count': max(token_counts),
            'min_token_count': min(token_counts),
            'total_tokens': sum(token_counts),
            'chunks_exceeding_limit': sum(1 for count in token_counts if count > self.chunk_size + self.overlap_size)
        }


def main():
    """Main function to demonstrate chunking functionality."""
    # Initialize chunker with 512-token chunks and 10% overlap (51 tokens)
    chunker = ChunkingStrategy(chunk_size=512, overlap_size=51)

    # Example text to chunk
    sample_text = """
# Introduction to Robotics

Robotics is an interdisciplinary field that integrates mechanical engineering, electrical engineering, computer science, and other disciplines to design, construct, operate, and use robots.

## History of Robotics

The concept of automated machines dates back to ancient civilizations. However, the modern era of robotics began in the 20th century with the development of programmable machines.

The first industrial robot, Unimate, was installed in 1961 at a General Motors plant. This marked the beginning of widespread use of robots in manufacturing.

## Types of Robots

There are several categories of robots:

- Industrial robots: Used in manufacturing and assembly lines
- Service robots: Assist humans in various tasks
- Medical robots: Used in surgeries and patient care
- Military robots: Used for reconnaissance and combat operations

### Industrial Robots

Industrial robots are the most common type of robot. They are typically used for welding, painting, assembly, and material handling tasks. These robots are designed for precision and reliability in repetitive tasks.

The main advantages of industrial robots include increased productivity, improved quality, and enhanced safety for human workers.

### Service Robots

Service robots are designed to assist humans in various non-manufacturing tasks. These include domestic robots like vacuum cleaners, entertainment robots, and professional service robots used in hospitals, hotels, and offices.

The service robot market has been growing rapidly with advances in artificial intelligence and human-robot interaction technologies.
"""

    # Chunk the sample text
    chunks = chunker.chunk_text(sample_text, "intro_to_robotics", "introduction", "Introduction to Robotics")

    # Print results
    print(f"Original text tokens: {chunker.count_tokens(sample_text)}")
    print(f"Number of chunks created: {len(chunks)}")

    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} (Tokens: {chunk.token_count}, Position: {chunk.position}):")
        print(f"ID: {chunk.id}")
        print(f"Content preview: {chunk.content[:100]}...")
        print("---")

    # Validate chunk quality
    validation = chunker.validate_chunk_quality(chunks)
    print(f"\nChunk Quality Validation:")
    print(f"Total chunks: {validation['total_chunks']}")
    print(f"Average tokens per chunk: {validation['avg_token_count']:.2f}")
    print(f"Max tokens in a chunk: {validation['max_token_count']}")
    print(f"Min tokens in a chunk: {validation['min_token_count']}")
    print(f"Total tokens: {validation['total_tokens']}")
    print(f"Chunks exceeding limit: {validation['chunks_exceeding_limit']}")


if __name__ == "__main__":
    main()