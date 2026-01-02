"""
Show Allowed AI Topics for Quiz Generation
Run: python show_allowed_topics.py
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from src.utils.ai_topics import is_ai_topic, get_ai_topic_suggestions

def show_allowed_topics():
    print("="*70)
    print("ALLOWED AI TOPICS FOR QUIZ GENERATION")
    print("="*70)
    
    print("\n1. SUGGESTED TOPICS (Available in Dropdown):")
    print("-" * 70)
    suggestions = get_ai_topic_suggestions()
    for i, topic in enumerate(suggestions, 1):
        print(f"   {i:2}. {topic}")
    
    print("\n2. VALIDATION EXAMPLES:")
    print("-" * 70)
    test_cases = [
        ("Machine Learning", True),
        ("Deep Learning", True),
        ("Neural Networks", True),
        ("NLP", True),
        ("Computer Vision", True),
        ("CNN", True),
        ("Transformers", True),
        ("Generative AI", True),
        ("Python Basics", False),
        ("Math", False),
        ("History", False),
        ("Data Structures", False),
        ("Introduction to Machine Learning", True),
        ("Deep Learning Applications", True),
        ("Neural Network Architecture", True),
    ]
    
    for topic, expected in test_cases:
        result = is_ai_topic(topic)
        status = "[ALLOWED]" if result else "[NOT ALLOWED]"
        match = "✓" if result == expected else "✗"
        print(f"   {match} {status:12} | {topic}")
    
    print("\n3. HOW IT WORKS:")
    print("-" * 70)
    print("   - System checks if topic contains AI-related keywords")
    print("   - Recognizes 100+ AI topics and keywords")
    print("   - Case-insensitive matching")
    print("   - Partial keyword matching (e.g., 'Machine Learning Basics' is allowed)")
    
    print("\n4. COMMON AI KEYWORDS RECOGNIZED:")
    print("-" * 70)
    keywords = [
        "AI", "Machine Learning", "Deep Learning", "Neural Network",
        "NLP", "Computer Vision", "Reinforcement Learning",
        "CNN", "RNN", "LSTM", "Transformer", "GAN", "BERT", "GPT"
    ]
    for i, keyword in enumerate(keywords, 1):
        print(f"   {keyword:25}", end="")
        if i % 3 == 0:
            print()
    print()
    
    print("\n" + "="*70)
    print("For complete list, see: ALLOWED_AI_TOPICS.md")
    print("="*70)

if __name__ == "__main__":
    show_allowed_topics()

