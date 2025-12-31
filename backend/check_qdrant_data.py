#!/usr/bin/env python3
"""
Test script to check if Qdrant has data when running in the same process as the server
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.qdrant_service import qdrant_service

async def check_qdrant_data():
    """Check if Qdrant has the ingested data."""
    print("Checking Qdrant data in server process...")

    try:
        # Check if collection exists
        collection_info = qdrant_service.get_collection_info()
        print(f"Collection info: {collection_info}")

        # Count points in collection
        count = qdrant_service.count_points()
        print(f"Number of points in collection: {count}")

        if count > 0:
            # Try to retrieve a few points to verify they exist
            try:
                # Get first few points
                results, _ = qdrant_service.scroll_collection(limit=3)
                print(f"Retrieved {len(results)} sample points")
                if results:
                    print("Sample point payload keys:", list(results[0]['payload'].keys()) if results[0]['payload'] else "No payload")
                    print("Sample content preview:", results[0]['payload'].get('content', '')[:100] if results[0]['payload'] else "No content")
            except Exception as e:
                print(f"Error retrieving sample points: {e}")

        return count > 0
    except Exception as e:
        print(f"Error checking Qdrant data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    has_data = asyncio.run(check_qdrant_data())
    print(f"Qdrant has data: {has_data}")