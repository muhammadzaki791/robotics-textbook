"""
Test script for selected-text functionality of the RAG Chatbot.
This script tests the selected-text mode implemented in Phase 4.
"""

import asyncio
import time
import requests
import json


def test_selected_text_functionality():
    """
    Test selected-text functionality with various text selections.
    """
    print("Testing Selected-Text Functionality...")

    # Sample selected texts and related questions
    test_cases = [
        {
            "selected_text": "Humanoid robots are robots with physical characteristics that resemble the human body.",
            "question": "What are humanoid robots?",
            "description": "Basic definition question"
        },
        {
            "selected_text": "Physical AI combines principles of artificial intelligence with physical systems and robotics.",
            "question": "How does Physical AI work?",
            "description": "Principle explanation"
        },
        {
            "selected_text": "Machine learning algorithms in robotics help robots adapt to new situations and improve performance.",
            "question": "Why are machine learning algorithms important in robotics?",
            "description": "Importance question"
        },
        {
            "selected_text": "Sensor fusion is the process of combining data from multiple sensors to create a more accurate understanding of the environment.",
            "question": "Explain sensor fusion.",
            "description": "Definition question"
        },
        {
            "selected_text": "This is a completely irrelevant text that has nothing to do with robotics or AI.",
            "question": "What is reinforcement learning?",
            "description": "Irrelevant text test"
        }
    ]

    api_url = "http://localhost:8000/chat/ask"  # Default API URL

    print(f"Testing against API endpoint: {api_url}")

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i} ({test_case['description']}):")
        print(f"  Selected text: '{test_case['selected_text'][:50]}{'...' if len(test_case['selected_text']) > 50 else ''}'")
        print(f"  Question: '{test_case['question']}'")

        start_time = time.time()

        try:
            response = requests.post(
                api_url,
                json={
                    "question": test_case['question'],
                    "selected_text": test_case['selected_text']
                },
                headers={"Content-Type": "application/json"},
                timeout=15  # 15 second timeout for more complex queries
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

                # Check if the answer seems to be related to the selected text
                answer_lower = answer.lower()
                selected_lower = test_case['selected_text'].lower()

                # Simple check: if selected text contains key terms, see if answer addresses them
                if any(term in selected_lower for term in ['humanoid', 'ai', 'robot', 'sensor', 'learning']):
                    if any(term in answer_lower for term in ['humanoid', 'ai', 'robot', 'sensor', 'learning', 'answer is not found']):
                        print(f"  ✅ Answer appears contextually relevant")
                    else:
                        print(f"  ⚠️  Answer may not be contextually relevant to selected text")
                else:
                    if "not found in the book" in answer_lower:
                        print(f"  ✅ Correctly returned 'not found' for irrelevant text")
                    else:
                        print(f"  ℹ️  Answer provided for potentially irrelevant text")

            else:
                print(f"  ❌ Error: HTTP {response.status_code}")
                print(f"  Response: {response.text}")

        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout error - request took more than 15 seconds")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection error - could not reach API at {api_url}")
            print(f"  Make sure the backend server is running on {api_url}")
            break
        except Exception as e:
            print(f"  ❌ Unexpected error: {str(e)}")

    print(f"\nSelected-text functionality test completed.")


def test_selected_text_restriction():
    """
    Test that responses are properly restricted to selected text content.
    """
    print("\nTesting Selected-Text Response Restriction...")

    # Test with selected text that should lead to specific answers
    restriction_tests = [
        {
            "selected_text": "The main components of a humanoid robot are actuators, sensors, and a control system.",
            "question": "What are the main components of a humanoid robot?",
            "expected_elements": ["actuators", "sensors", "control system"]
        },
        {
            "selected_text": "Reinforcement learning is a type of machine learning where an agent learns to make decisions by performing actions and receiving rewards.",
            "question": "How does reinforcement learning work?",
            "expected_elements": ["agent", "actions", "rewards", "decisions"]
        }
    ]

    api_url = "http://localhost:8000/chat/ask"

    for i, test in enumerate(restriction_tests, 1):
        print(f"\nRestriction Test {i}:")
        print(f"  Selected text: '{test['selected_text'][:60]}...'")
        print(f"  Question: '{test['question']}'")

        try:
            response = requests.post(
                api_url,
                json={
                    "question": test['question'],
                    "selected_text": test['selected_text']
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "").lower()

                print(f"  Answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")

                # Check if the answer contains expected elements from the selected text
                found_elements = []
                for element in test['expected_elements']:
                    if element.lower() in answer:
                        found_elements.append(element)

                if found_elements:
                    print(f"  ✅ Found expected elements: {found_elements}")
                else:
                    print(f"  ⚠️  Expected elements {test['expected_elements']} not found in answer")

            else:
                print(f"  ❌ Error: HTTP {response.status_code}")

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

    print(f"\nResponse restriction test completed.")


if __name__ == "__main__":
    print("Starting RAG Chatbot Selected-Text Tests\n")

    # Note: This test assumes the backend server is running
    # You need to start the backend server before running this test
    print("IMPORTANT: Make sure the backend server is running before executing this test!")
    print("Start the server with: cd backend && python -m src.api.main")
    print("-" * 70)

    test_selected_text_functionality()
    test_selected_text_restriction()

    print("\n" + "="*70)
    print("Test execution completed. Check results above for any issues.")