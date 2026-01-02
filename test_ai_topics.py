"""
Test AI Topics Validator
Run: python test_ai_topics.py
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from src.utils.ai_topics import is_ai_topic, get_ai_topic_suggestions

def test_ai_topics():
    print("="*60)
    print("AI Topic Validator Test")
    print("="*60)
    
    # Test cases
    test_cases = [
        ("Machine Learning", True),
        ("Deep Learning", True),
        ("Neural Networks", True),
        ("Natural Language Processing", True),
        ("NLP", True),
        ("Computer Vision", True),
        ("Python Basics", False),
        ("Math", False),
        ("History", False),
        ("Data Structures", False),
        ("Algorithms", False),
        ("Reinforcement Learning", True),
        ("CNN", True),
        ("Transformers", True),
        ("Generative AI", True),
    ]
    
    print("\nTesting topic validation:")
    print("-" * 60)
    all_passed = True
    for topic, expected in test_cases:
        result = is_ai_topic(topic)
        status = "[PASS]" if result == expected else "[FAIL]"
        if result != expected:
            all_passed = False
        print(f"{status} | {topic:30} | Expected: {expected:5} | Got: {result:5}")
    
    print("\n" + "="*60)
    if all_passed:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED!")
    
    print("\nAI Topic Suggestions:")
    print("-" * 60)
    for topic in get_ai_topic_suggestions():
        print(f"  - {topic}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(test_ai_topics())

