"""
Test script for basic Q&A functionality of the RAG Chatbot.
This script tests the core functionality implemented in Phase 3.
"""

import asyncio
import time
import requests
import json


def test_basic_qa_functionality():
    """
    Test basic Q&A functionality with sample textbook questions.
    """
    print("Testing Basic Q&A Functionality...")

    # Sample questions that might be relevant to a Physical AI & Humanoid Robotics textbook
    sample_questions = [
        "What is humanoid robotics?",
        "Explain the principles of physical AI.",
        "How do robots maintain balance?",
        "What sensors are used in humanoid robots?",
        "Explain motor control in robotics.",
        "This is a random question not related to the textbook content",
        "Tell me about reinforcement learning in robotics"
    ]

    api_url = "http://localhost:8000/chat/ask"  # Default API URL

    print(f"Testing against API endpoint: {api_url}")

    for i, question in enumerate(sample_questions, 1):
        print(f"\nTest {i}: Question: '{question}'")

        start_time = time.time()

        try:
            response = requests.post(
                api_url,
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=10  # 10 second timeout
            )

            end_time = time.time()
            response_time = end_time - start_time

            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "No answer provided")
                sources = data.get("sources", [])

                print(f"  Response time: {response_time:.2f} seconds")
                print(f"  Answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                print(f"  Sources: {len(sources)} cited")

                # Check if response time is under 2 seconds (requirement from T39)
                if response_time > 2:
                    print(f"  ⚠️  WARNING: Response time ({response_time:.2f}s) exceeds 2-second requirement")
                else:
                    print(f"  ✅ Response time requirement met (< 2s)")

                # Check for "not found" responses (requirement from T040)
                if "not found in the book" in answer.lower():
                    print(f"  ✅ Correctly returned 'not found' for irrelevant question")
                else:
                    print(f"  ℹ️  Relevant answer provided for potentially relevant question")

            else:
                print(f"  ❌ Error: HTTP {response.status_code}")
                print(f"  Response: {response.text}")

        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout error - request took more than 10 seconds")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection error - could not reach API at {api_url}")
            print(f"  Make sure the backend server is running on {api_url}")
            break
        except Exception as e:
            print(f"  ❌ Unexpected error: {str(e)}")

    print(f"\nBasic Q&A functionality test completed.")


def test_not_found_responses():
    """
    Test that the system properly returns 'not found' responses when content is unavailable.
    """
    print("\nTesting 'Not Found' Response Functionality...")

    # Questions that are very unlikely to be in a robotics textbook
    irrelevant_questions = [
        "What is the capital of France?",
        "How do I bake a chocolate cake?",
        "Explain quantum physics in simple terms.",
        "What are the lyrics to 'Bohemian Rhapsody'?",
        "How to install Windows 11 on a Mac?"
    ]

    api_url = "http://localhost:8000/chat/ask"

    success_count = 0

    for question in irrelevant_questions:
        try:
            response = requests.post(
                api_url,
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")

                if "not found in the book" in answer.lower():
                    print(f"  ✅ Correctly returned 'not found' for: '{question[:30]}...'")
                    success_count += 1
                else:
                    print(f"  ❌ Incorrectly provided answer for: '{question[:30]}...'")
            else:
                print(f"  ❌ Error for question '{question[:30]}...': HTTP {response.status_code}")

        except Exception as e:
            print(f"  ❌ Error testing question '{question[:30]}...': {str(e)}")

    print(f"\n'Not found' response test: {success_count}/{len(irrelevant_questions)} successful")


if __name__ == "__main__":
    print("Starting RAG Chatbot Basic Q&A Tests\n")

    # Note: This test assumes the backend server is running
    # You need to start the backend server before running this test
    print("IMPORTANT: Make sure the backend server is running before executing this test!")
    print("Start the server with: cd backend && python -m src.api.main")
    print("-" * 60)

    test_basic_qa_functionality()
    test_not_found_responses()

    print("\n" + "="*60)
    print("Test execution completed. Check results above for any issues.")