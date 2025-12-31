"""
Content Exporter for RAG Chatbot

This module handles the export and listing of all textbook Markdown files
for ingestion into the RAG system.
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import markdown
from bs4 import BeautifulSoup


class ContentExporter:
    """Handles exporting and processing textbook content for RAG ingestion."""

    def __init__(self, textbook_path: str):
        """
        Initialize the ContentExporter.

        Args:
            textbook_path: Path to the textbook directory containing Markdown files
        """
        self.textbook_path = Path(textbook_path)

    def find_textbook_files(self, extensions: List[str] = None) -> List[Path]:
        """
        Find all textbook files in the specified directory.

        Args:
            extensions: List of file extensions to look for (default: ['.md'])

        Returns:
            List of Path objects for all found files
        """
        if extensions is None:
            extensions = ['.md']

        files = []
        for ext in extensions:
            # Search recursively in the textbook directory
            pattern = f"**/*{ext}"
            for file_path in self.textbook_path.glob(pattern):
                files.append(file_path)

        return sorted(files)

    def extract_content(self, file_path: Path) -> Dict[str, str]:
        """
        Extract content from a Markdown file.

        Args:
            file_path: Path to the Markdown file

        Returns:
            Dictionary containing file info and content
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Generate a document ID based on the file path
        relative_path = file_path.relative_to(self.textbook_path)
        document_id = str(relative_path).replace('/', '_').replace('\\', '_').replace('.md', '')

        # Extract title from the first heading
        title = self._extract_title(content)

        return {
            'document_id': document_id,
            'file_path': str(file_path),
            'relative_path': str(relative_path),
            'title': title,
            'content': content,
            'chapter': self._extract_chapter(str(relative_path))
        }

    def _extract_title(self, content: str) -> str:
        """
        Extract the title from Markdown content (first heading).

        Args:
            content: Markdown content as string

        Returns:
            Extracted title or empty string if not found
        """
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                return line.strip()[2:]  # Remove '# ' prefix
        return ''

    def _extract_chapter(self, relative_path: str) -> str:
        """
        Extract chapter name from the relative path.

        Args:
            relative_path: Relative path of the file

        Returns:
            Chapter name
        """
        parts = relative_path.split(os.sep)
        # The first part after 'robotics-textbook' is usually the chapter
        if len(parts) > 1:
            return parts[0]
        return 'unknown'

    def export_all_content(self) -> List[Dict[str, str]]:
        """
        Export all content from textbook files.

        Returns:
            List of dictionaries containing file info and content
        """
        files = self.find_textbook_files()
        all_content = []

        for file_path in files:
            try:
                content_data = self.extract_content(file_path)
                all_content.append(content_data)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        return all_content

    def generate_content_report(self) -> Dict[str, any]:
        """
        Generate a report about the textbook content.

        Returns:
            Dictionary containing content statistics
        """
        files = self.find_textbook_files()
        content_list = self.export_all_content()

        # Calculate statistics
        total_files = len(files)
        total_chars = sum(len(item['content']) for item in content_list)
        total_words = sum(len(item['content'].split()) for item in content_list)

        # Group by chapter
        chapters = {}
        for item in content_list:
            chapter = item['chapter']
            if chapter not in chapters:
                chapters[chapter] = []
            chapters[chapter].append(item)

        return {
            'total_files': total_files,
            'total_characters': total_chars,
            'total_words': total_words,
            'chapters': list(chapters.keys()),
            'chapter_counts': {chapter: len(items) for chapter, items in chapters.items()},
            'files': [item['relative_path'] for item in content_list]
        }


def main():
    """Main function to demonstrate content export functionality."""
    # Set the textbook path
    textbook_path = "C:/Users/dell/OneDrive/Desktop/Zaki-Projects/Q4/New folder/Book/docs/robotics-textbook"

    # Create content exporter
    exporter = ContentExporter(textbook_path)

    # Export all content
    all_content = exporter.export_all_content()

    # Generate report
    report = exporter.generate_content_report()

    print("Textbook Content Report:")
    print(f"Total files: {report['total_files']}")
    print(f"Total characters: {report['total_characters']}")
    print(f"Total words: {report['total_words']}")
    print(f"Chapters: {', '.join(report['chapters'])}")
    print(f"Chapter breakdown: {report['chapter_counts']}")

    # Print first few files as examples
    print("\nFirst few files:")
    for i, content in enumerate(all_content[:5]):
        print(f"{i+1}. {content['relative_path']} - '{content['title']}'")

    # Save the list of files to a text file for ingestion pipeline
    with open("textbook_files_list.txt", "w", encoding="utf-8") as f:
        for content in all_content:
            f.write(f"{content['file_path']}\n")

    print(f"\nList of {len(all_content)} files saved to textbook_files_list.txt")

    return all_content


if __name__ == "__main__":
    main()