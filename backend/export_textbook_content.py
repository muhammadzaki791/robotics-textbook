"""
Export Textbook Content for RAG Ingestion

This script identifies and exports all textbook Markdown files for the RAG system.
"""
import os
from pathlib import Path
import json
from typing import List, Dict


def find_textbook_markdown_files(textbook_dir: str) -> List[Dict[str, str]]:
    """
    Find all Markdown files in the textbook directory structure.

    Args:
        textbook_dir: Path to the textbook directory

    Returns:
        List of dictionaries containing file information
    """
    textbook_path = Path(textbook_dir)
    markdown_files = []

    # Find all .md files recursively
    for md_file in textbook_path.rglob("*.md"):
        # Skip index files if they're just navigation (optional)
        # Include all content files
        relative_path = md_file.relative_to(textbook_path)

        # Create document ID from the path
        doc_id = str(relative_path).replace(os.sep, '_').replace('.md', '')

        # Extract chapter from path (first directory level)
        path_parts = str(relative_path).split(os.sep)
        chapter = path_parts[0] if path_parts else 'unknown'

        # Extract title from content (first heading)
        title = extract_title_from_file(md_file)

        file_info = {
            'document_id': doc_id,
            'file_path': str(md_file),
            'relative_path': str(relative_path),
            'title': title,
            'chapter': chapter,
            'url_path': str(relative_path).replace('.md', '').replace(os.sep, '/')
        }

        markdown_files.append(file_info)

    return sorted(markdown_files, key=lambda x: x['relative_path'])


def extract_title_from_file(file_path: Path) -> str:
    """
    Extract the title from a Markdown file (first heading).

    Args:
        file_path: Path to the Markdown file

    Returns:
        Extracted title or empty string if not found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for the first heading
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()  # Remove '# ' and return title
            elif line.startswith('#'):
                # Handle other heading levels if no level 1 heading found
                continue

        # If no heading found, use the filename as title
        return file_path.stem.replace('-', ' ').replace('_', ' ').title()
    except Exception:
        return file_path.stem


def export_file_list(textbook_dir: str, output_file: str = "textbook_content_files.json"):
    """
    Export the list of textbook files to a JSON file.

    Args:
        textbook_dir: Path to the textbook directory
        output_file: Output file name for the JSON export
    """
    print(f"Exporting textbook content files from: {textbook_dir}")

    # Find all markdown files
    files = find_textbook_markdown_files(textbook_dir)

    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(files, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(files)} files to {output_file}")

    # Print summary
    chapters = set(file['chapter'] for file in files)
    print(f"Found content in {len(chapters)} chapters: {', '.join(sorted(chapters))}")

    return files


def create_simple_file_list(textbook_dir: str, output_file: str = "textbook_files.txt"):
    """
    Create a simple text file with paths to all textbook Markdown files.

    Args:
        textbook_dir: Path to the textbook directory
        output_file: Output file name for the text export
    """
    files = find_textbook_markdown_files(textbook_dir)

    with open(output_file, 'w', encoding='utf-8') as f:
        for file_info in files:
            f.write(file_info['file_path'] + '\n')

    print(f"Created simple file list with {len(files)} entries: {output_file}")


def main():
    """Main function to export textbook content."""
    # Set the textbook directory path
    textbook_dir = "C:/Users/dell/OneDrive/Desktop/Zaki-Projects/Q4/New folder/Book/docs/robotics-textbook"

    # Export to JSON format
    json_files = export_file_list(textbook_dir, "textbook_content_files.json")

    # Create simple text file list
    create_simple_file_list(textbook_dir, "textbook_files.txt")

    # Print some examples
    print("\nFirst 5 files:")
    for i, file_info in enumerate(json_files[:5]):
        print(f"{i+1}. {file_info['relative_path']} (Chapter: {file_info['chapter']})")

    print(f"\nTotal files ready for ingestion: {len(json_files)}")


if __name__ == "__main__":
    main()