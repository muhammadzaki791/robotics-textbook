"""
Chunk Quality Validation Module

This module provides comprehensive validation and quality metrics for text chunks
used in the RAG system. It evaluates chunk quality based on multiple criteria
to ensure optimal retrieval performance.
"""
import json
import re
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from collections import Counter
import statistics

from src.utils.chunking import DocumentChunk


@dataclass
class ValidationMetrics:
    """Data class to hold validation metrics."""
    total_chunks: int
    total_documents: int
    avg_tokens_per_chunk: float
    min_tokens_per_chunk: int
    max_tokens_per_chunk: int
    median_tokens_per_chunk: float
    token_count_std_dev: float

    # Quality metrics
    chunks_below_min_threshold: int  # Chunks with <50 tokens
    chunks_above_max_threshold: int  # Chunks exceeding chunk_size + overlap
    avg_chunk_quality_score: float   # Overall quality score (0-1)

    # Semantic boundary metrics
    header_preservation_rate: float   # Rate of preserved headers
    paragraph_separation_rate: float  # Rate of preserved paragraphs
    section_continuity: float         # How well sections flow

    # Content metrics
    avg_word_count: float
    avg_sentence_count: float
    readability_score: float          # Estimated readability
    content_diversity: float          # How diverse the content is

    # Metadata completeness
    metadata_completeness: float      # How complete the metadata is
    document_coverage: float          # Coverage of all documents

    # Detailed breakdown
    chunk_size_distribution: Dict[str, int]  # Distribution of chunk sizes
    quality_issues: List[str]                # List of identified issues


class ChunkValidator:
    """Validates the quality of text chunks for RAG system."""

    def __init__(self, min_tokens: int = 50, max_tokens: int = 563,  # 512 + 51 overlap
                 min_word_count: int = 25, max_chunk_ratio: float = 1.2):
        """
        Initialize the chunk validator.

        Args:
            min_tokens: Minimum number of tokens for a valid chunk
            max_tokens: Maximum number of tokens for a valid chunk
            min_word_count: Minimum word count for a valid chunk
            max_chunk_ratio: Maximum ratio of chunk size to average size
        """
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.min_word_count = min_word_count
        self.max_chunk_ratio = max_chunk_ratio

    def validate_chunks(self, chunks: List[DocumentChunk]) -> ValidationMetrics:
        """
        Validate a list of chunks and return quality metrics.

        Args:
            chunks: List of DocumentChunk objects to validate

        Returns:
            ValidationMetrics object with quality metrics
        """
        if not chunks:
            return self._empty_metrics()

        # Extract token counts
        token_counts = [chunk.token_count for chunk in chunks]
        avg_tokens = statistics.mean(token_counts)
        median_tokens = statistics.median(token_counts)

        # Calculate standard deviation
        if len(token_counts) > 1:
            token_std_dev = statistics.stdev(token_counts)
        else:
            token_std_dev = 0.0

        # Count chunks outside thresholds
        chunks_below_min = sum(1 for count in token_counts if count < self.min_tokens)
        chunks_above_max = sum(1 for count in token_counts if count > self.max_tokens)

        # Calculate quality metrics
        quality_score = self._calculate_quality_score(chunks)
        header_preservation = self._calculate_header_preservation(chunks)
        paragraph_separation = self._calculate_paragraph_separation(chunks)
        section_continuity = self._calculate_section_continuity(chunks)

        # Content metrics
        avg_word_count = self._calculate_avg_word_count(chunks)
        avg_sentence_count = self._calculate_avg_sentence_count(chunks)
        readability_score = self._calculate_readability_score(chunks)
        content_diversity = self._calculate_content_diversity(chunks)

        # Metadata metrics
        metadata_completeness = self._calculate_metadata_completeness(chunks)
        document_coverage = self._calculate_document_coverage(chunks)

        # Distribution of chunk sizes
        chunk_size_distribution = self._calculate_size_distribution(token_counts)

        # Identify quality issues
        quality_issues = self._identify_quality_issues(chunks)

        # Calculate unique document count
        unique_documents = len(set(chunk.document_id for chunk in chunks))

        return ValidationMetrics(
            total_chunks=len(chunks),
            total_documents=unique_documents,
            avg_tokens_per_chunk=avg_tokens,
            min_tokens_per_chunk=min(token_counts),
            max_tokens_per_chunk=max(token_counts),
            median_tokens_per_chunk=median_tokens,
            token_count_std_dev=token_std_dev,
            chunks_below_min_threshold=chunks_below_min,
            chunks_above_max_threshold=chunks_above_max,
            avg_chunk_quality_score=quality_score,
            header_preservation_rate=header_preservation,
            paragraph_separation_rate=paragraph_separation,
            section_continuity=section_continuity,
            avg_word_count=avg_word_count,
            avg_sentence_count=avg_sentence_count,
            readability_score=readability_score,
            content_diversity=content_diversity,
            metadata_completeness=metadata_completeness,
            document_coverage=document_coverage,
            chunk_size_distribution=chunk_size_distribution,
            quality_issues=quality_issues
        )

    def _empty_metrics(self) -> ValidationMetrics:
        """Return empty metrics when no chunks are provided."""
        return ValidationMetrics(
            total_chunks=0,
            total_documents=0,
            avg_tokens_per_chunk=0,
            min_tokens_per_chunk=0,
            max_tokens_per_chunk=0,
            median_tokens_per_chunk=0,
            token_count_std_dev=0,
            chunks_below_min_threshold=0,
            chunks_above_max_threshold=0,
            avg_chunk_quality_score=0,
            header_preservation_rate=0,
            paragraph_separation_rate=0,
            section_continuity=0,
            avg_word_count=0,
            avg_sentence_count=0,
            readability_score=0,
            content_diversity=0,
            metadata_completeness=0,
            document_coverage=0,
            chunk_size_distribution={},
            quality_issues=[]
        )

    def _calculate_quality_score(self, chunks: List[DocumentChunk]) -> float:
        """
        Calculate an overall quality score for the chunks.

        Args:
            chunks: List of DocumentChunk objects

        Returns:
            Quality score between 0 and 1
        """
        if not chunks:
            return 0.0

        scores = []
        for chunk in chunks:
            # Base score on token count being in good range
            if self.min_tokens <= chunk.token_count <= self.max_tokens:
                token_score = 1.0
            elif chunk.token_count < self.min_tokens:
                # Lower score for too small chunks
                token_score = max(0.0, chunk.token_count / self.min_tokens)
            else:
                # Lower score for too large chunks
                token_score = max(0.0, 1.0 - (chunk.token_count - self.max_tokens) / self.max_tokens)

            # Consider content quality
            content_score = self._assess_content_quality(chunk.content)

            # Average the scores
            avg_score = (token_score + content_score) / 2.0
            scores.append(avg_score)

        return statistics.mean(scores) if scores else 0.0

    def _assess_content_quality(self, content: str) -> float:
        """
        Assess the quality of content in a chunk.

        Args:
            content: Chunk content to assess

        Returns:
            Quality score between 0 and 1
        """
        if not content.strip():
            return 0.0

        # Check for meaningful content (not just whitespace or special characters)
        meaningful_content_ratio = len(content.strip()) / len(content) if content else 0

        # Check for headers
        header_ratio = len(re.findall(r'^#+\s.*$', content, re.MULTILINE)) / max(content.count('\n'), 1) if content.count('\n') > 0 else 0

        # Check for proper sentences
        sentence_ratio = len(re.findall(r'[.!?]+\s', content)) / max(content.count('\n'), 1) if content.count('\n') > 0 else 0

        # Combine scores
        return (meaningful_content_ratio + header_ratio + sentence_ratio) / 3.0

    def _calculate_header_preservation(self, chunks: List[DocumentChunk]) -> float:
        """
        Calculate the rate of preserved headers in chunks.

        Args:
            chunks: List of DocumentChunk objects

        Returns:
            Header preservation rate (0-1)
        """
        if not chunks:
            return 0.0

        total_chunks = len(chunks)
        chunks_with_headers = sum(1 for chunk in chunks if re.search(r'^#+\s.*$', chunk.content, re.MULTILINE))

        return chunks_with_headers / total_chunks if total_chunks > 0 else 0.0

    def _calculate_paragraph_separation(self, chunks: List[DocumentChunk]) -> float:
        """
        Calculate the rate of preserved paragraph separation.

        Args:
            chunks: List of DocumentChunk objects

        Returns:
            Paragraph separation rate (0-1)
        """
        if not chunks:
            return 0.0

        total_chunks = len(chunks)
        well_separated = 0

        for chunk in chunks:
            # Count paragraph breaks (double newlines)
            paragraph_breaks = chunk.content.count('\n\n')
            # Count total newlines
            total_newlines = chunk.content.count('\n')

            if total_newlines > 0:
                separation_ratio = paragraph_breaks / total_newlines
                # Consider it well-separated if there's a good ratio of paragraph breaks
                if separation_ratio >= 0.3:  # At least 30% of newlines are paragraph breaks
                    well_separated += 1

        return well_separated / total_chunks if total_chunks > 0 else 0.0

    def _calculate_section_continuity(self, chunks: List[DocumentChunk]) -> float:
        """
        Calculate how well sections flow from one chunk to another.

        Args:
            chunks: List of DocumentChunk objects

        Returns:
            Section continuity score (0-1)
        """
        if len(chunks) < 2:
            return 1.0 if len(chunks) == 1 else 0.0

        # Group chunks by document
        chunks_by_doc = {}
        for chunk in chunks:
            if chunk.document_id not in chunks_by_doc:
                chunks_by_doc[chunk.document_id] = []
            chunks_by_doc[chunk.document_id].append(chunk)

        # For each document, check continuity
        continuity_scores = []
        for doc_chunks in chunks_by_doc.values():
            # Sort by position
            sorted_chunks = sorted(doc_chunks, key=lambda x: x.position)

            # Check how many consecutive chunks have semantic continuity
            continuous_pairs = 0
            total_pairs = max(1, len(sorted_chunks) - 1)

            for i in range(len(sorted_chunks) - 1):
                current = sorted_chunks[i]
                next_chunk = sorted_chunks[i + 1]

                # Check if the current chunk ends with a complete thought
                ends_with_sentence_end = bool(re.search(r'[.!?]\s*$', current.content.strip()))
                starts_with_sentence_start = bool(re.match(r'^\s*[A-Z][a-z]', next_chunk.content))

                # If current ends with sentence end and next starts with capital, likely continuous
                if ends_with_sentence_end and starts_with_sentence_start:
                    continuous_pairs += 1

            continuity_scores.append(continuous_pairs / total_pairs)

        return statistics.mean(continuity_scores) if continuity_scores else 0.0

    def _calculate_avg_word_count(self, chunks: List[DocumentChunk]) -> float:
        """Calculate average word count per chunk."""
        if not chunks:
            return 0.0

        word_counts = [len(chunk.content.split()) for chunk in chunks]
        return statistics.mean(word_counts)

    def _calculate_avg_sentence_count(self, chunks: List[DocumentChunk]) -> float:
        """Calculate average sentence count per chunk."""
        if not chunks:
            return 0.0

        sentence_counts = []
        for chunk in chunks:
            # Count sentences by looking for sentence endings
            sentences = re.split(r'[.!?]+', chunk.content)
            # Filter out empty strings
            sentences = [s.strip() for s in sentences if s.strip()]
            sentence_counts.append(len(sentences))

        return statistics.mean(sentence_counts) if sentence_counts else 0.0

    def _calculate_readability_score(self, chunks: List[DocumentChunk]) -> float:
        """
        Calculate a basic readability score based on sentence and word complexity.
        This is a simplified version - in practice, you might use a more sophisticated library.
        """
        if not chunks:
            return 0.0

        scores = []
        for chunk in chunks:
            sentences = re.split(r'[.!?]+', chunk.content)
            sentences = [s.strip() for s in sentences if s.strip()]
            sentence_count = len(sentences)

            if sentence_count == 0:
                continue

            words = chunk.content.split()
            word_count = len(words)

            if word_count == 0:
                continue

            avg_words_per_sentence = word_count / sentence_count

            # Simplified readability score (Flesch reading ease approximation)
            # Higher scores indicate easier reading
            score = 206.835 - (1.015 * avg_words_per_sentence)  # Simplified version
            # Normalize to 0-1 range
            score = max(0, min(1, (score + 10) / 110))  # Adjusted to fit 0-1 range
            scores.append(score)

        return statistics.mean(scores) if scores else 0.0

    def _calculate_content_diversity(self, chunks: List[DocumentChunk]) -> float:
        """Calculate content diversity across chunks."""
        if not chunks:
            return 0.0

        # Get all unique words across all chunks
        all_words = set()
        for chunk in chunks:
            words = set(re.findall(r'\b\w+\b', chunk.content.lower()))
            all_words.update(words)

        # Calculate average unique words per chunk
        total_unique_words = len(all_words)
        avg_words_per_chunk = self._calculate_avg_word_count(chunks)

        # Diversity score based on ratio of unique words to average chunk size
        if avg_words_per_chunk > 0:
            diversity = min(1.0, total_unique_words / (avg_words_per_chunk * len(chunks) * 0.1))
        else:
            diversity = 0.0

        return diversity

    def _calculate_metadata_completeness(self, chunks: List[DocumentChunk]) -> float:
        """Calculate how complete the metadata is."""
        if not chunks:
            return 0.0

        if not chunks[0].metadata:
            return 0.0

        # Define required metadata fields
        required_fields = ['source_file', 'relative_path', 'title', 'chapter']
        total_fields = len(required_fields) * len(chunks)
        present_fields = 0

        for chunk in chunks:
            for field in required_fields:
                if field in chunk.metadata and chunk.metadata[field]:
                    present_fields += 1

        return present_fields / total_fields if total_fields > 0 else 0.0

    def _calculate_document_coverage(self, chunks: List[DocumentChunk]) -> float:
        """Calculate document coverage."""
        if not chunks:
            return 0.0

        # For this metric, we consider all chunks as covering their respective documents
        # In a real scenario, you might compare against a list of all expected documents
        unique_documents = len(set(chunk.document_id for chunk in chunks))
        # Since we only have the documents that were chunked, coverage is 100% of what we have
        return 1.0

    def _calculate_size_distribution(self, token_counts: List[int]) -> Dict[str, int]:
        """Calculate distribution of chunk sizes."""
        if not token_counts:
            return {}

        # Define size ranges
        ranges = [
            (0, 50, "very_small"),
            (51, 150, "small"),
            (151, 300, "medium"),
            (301, 500, "large"),
            (501, 600, "very_large"),
            (601, float('inf'), "huge")
        ]

        distribution = {name: 0 for _, _, name in ranges}

        for count in token_counts:
            for min_val, max_val, name in ranges:
                if min_val <= count <= max_val:
                    distribution[name] += 1
                    break

        return distribution

    def _identify_quality_issues(self, chunks: List[DocumentChunk]) -> List[str]:
        """Identify specific quality issues in chunks."""
        issues = []

        for i, chunk in enumerate(chunks):
            # Check for very small chunks
            if chunk.token_count < self.min_tokens:
                issues.append(f"Chunk {i} ({chunk.id}): Too small ({chunk.token_count} tokens < {self.min_tokens})")

            # Check for very large chunks
            if chunk.token_count > self.max_tokens:
                issues.append(f"Chunk {i} ({chunk.id}): Too large ({chunk.token_count} tokens > {self.max_tokens})")

            # Check for chunks with no content
            if not chunk.content.strip():
                issues.append(f"Chunk {i} ({chunk.id}): Empty content")

            # Check for chunks with only special characters
            if chunk.content.strip() and not re.search(r'[a-zA-Z0-9]', chunk.content):
                issues.append(f"Chunk {i} ({chunk.id}): Only special characters")

            # Check for incomplete sentences
            if chunk.content.strip() and not re.search(r'[.!?]\s*$', chunk.content.strip()):
                # But don't flag if it's the last chunk of a document
                # This would require checking document structure, so we'll skip for now

                # For now, just note if there are no sentence endings at all
                if not re.search(r'[.!?]', chunk.content):
                    issues.append(f"Chunk {i} ({chunk.id}): No sentence endings")

        return issues

    def generate_detailed_report(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Generate a detailed validation report.

        Args:
            chunks: List of DocumentChunk objects

        Returns:
            Detailed validation report
        """
        metrics = self.validate_chunks(chunks)

        report = {
            "summary": {
                "total_chunks": metrics.total_chunks,
                "total_documents": metrics.total_documents,
                "avg_tokens_per_chunk": round(metrics.avg_tokens_per_chunk, 2),
                "token_std_dev": round(metrics.token_count_std_dev, 2),
                "quality_score": round(metrics.avg_chunk_quality_score, 3)
            },
            "token_analysis": {
                "min_tokens": metrics.min_tokens_per_chunk,
                "max_tokens": metrics.max_tokens_per_chunk,
                "median_tokens": metrics.median_tokens_per_chunk,
                "chunks_below_threshold": metrics.chunks_below_min_threshold,
                "chunks_above_threshold": metrics.chunks_above_max_threshold
            },
            "content_quality": {
                "header_preservation_rate": round(metrics.header_preservation_rate, 3),
                "paragraph_separation_rate": round(metrics.paragraph_separation_rate, 3),
                "section_continuity": round(metrics.section_continuity, 3),
                "avg_word_count": round(metrics.avg_word_count, 2),
                "avg_sentence_count": round(metrics.avg_sentence_count, 2),
                "readability_score": round(metrics.readability_score, 3),
                "content_diversity": round(metrics.content_diversity, 3)
            },
            "metadata_quality": {
                "completeness": round(metrics.metadata_completeness, 3),
                "document_coverage": round(metrics.document_coverage, 3)
            },
            "size_distribution": metrics.chunk_size_distribution,
            "quality_issues": metrics.quality_issues,
            "recommendations": self._generate_recommendations(metrics)
        }

        return report

    def _generate_recommendations(self, metrics: ValidationMetrics) -> List[str]:
        """Generate recommendations based on validation metrics."""
        recommendations = []

        if metrics.chunks_below_min_threshold > 0:
            pct_small = (metrics.chunks_below_min_threshold / metrics.total_chunks) * 100
            if pct_small > 10:  # More than 10% are too small
                recommendations.append(f"{pct_small:.1f}% of chunks are below minimum size. Consider reducing overlap or adjusting chunking strategy.")

        if metrics.chunks_above_max_threshold > 0:
            pct_large = (metrics.chunks_above_max_threshold / metrics.total_chunks) * 100
            if pct_large > 5:  # More than 5% are too large
                recommendations.append(f"{pct_large:.1f}% of chunks exceed maximum size. Consider adjusting chunking parameters.")

        if metrics.avg_chunk_quality_score < 0.7:  # Quality score below 70%
            recommendations.append(f"Overall quality score is low ({metrics.avg_chunk_quality_score:.3f}). Review chunking strategy.")

        if metrics.header_preservation_rate < 0.5:  # Less than 50% preserve headers
            recommendations.append(f"Header preservation is low ({metrics.header_preservation_rate:.3f}). Consider adjusting semantic boundary detection.")

        if metrics.metadata_completeness < 0.9:  # Less than 90% metadata complete
            recommendations.append(f"Metadata completeness is low ({metrics.metadata_completeness:.3f}). Ensure all required metadata is captured.")

        if not recommendations:
            recommendations.append("All validation metrics are within acceptable ranges.")

        return recommendations


def main():
    """Main function to demonstrate chunk validation."""
    # Example usage with sample chunks
    # In practice, you would load chunks from your chunking process
    from src.utils.chunking import DocumentChunk

    # Create sample chunks for testing
    sample_chunks = [
        DocumentChunk(
            id="doc1_chunk_0",
            content="# Introduction to Robotics\n\nRobotics is an interdisciplinary field...",
            document_id="doc1",
            chapter="introduction",
            section_title="Introduction to Robotics",
            position=0,
            token_count=120,
            metadata={"source_file": "intro.md", "relative_path": "intro.md"}
        ),
        DocumentChunk(
            id="doc1_chunk_1",
            content="The history of robotics dates back to ancient civilizations...",
            document_id="doc1",
            chapter="introduction",
            section_title="History of Robotics",
            position=1,
            token_count=95,
            metadata={"source_file": "intro.md", "relative_path": "intro.md"}
        ),
        DocumentChunk(
            id="doc2_chunk_0",
            content="# Types of Robots\n\nThere are several categories of robots:\n\n- Industrial robots...",
            document_id="doc2",
            chapter="robot_types",
            section_title="Types of Robots",
            position=0,
            token_count=200,
            metadata={"source_file": "types.md", "relative_path": "types.md"}
        )
    ]

    # Initialize validator
    validator = ChunkValidator()

    # Validate chunks
    metrics = validator.validate_chunks(sample_chunks)

    # Print summary
    print("Chunk Validation Summary:")
    print(f"Total chunks: {metrics.total_chunks}")
    print(f"Total documents: {metrics.total_documents}")
    print(f"Average tokens per chunk: {metrics.avg_tokens_per_chunk:.2f}")
    print(f"Quality score: {metrics.avg_chunk_quality_score:.3f}")
    print(f"Chunks below threshold: {metrics.chunks_below_min_threshold}")
    print(f"Chunks above threshold: {metrics.chunks_above_max_threshold}")

    # Generate detailed report
    report = validator.generate_detailed_report(sample_chunks)

    print("\nDetailed Report:")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()