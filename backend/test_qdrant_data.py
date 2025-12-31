#!/usr/bin/env python3
"""
Quick test to check if Qdrant has any data
"""
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.qdrant_service import qdrant_service

def test_qdrant():
    try:
        print("Starting Qdrant in local persistent mode...")
        count = qdrant_service.count_points()
        print(f"Number of points in collection: {count}")

        if count > 0:
            info = qdrant_service.get_collection_info()
            print(f"Collection info: {info}")
            return True
        else:
            print("No data found in Qdrant database")
            return False
    except Exception as e:
        print(f"Error accessing Qdrant: {e}")
        return False

if __name__ == "__main__":
    test_qdrant()