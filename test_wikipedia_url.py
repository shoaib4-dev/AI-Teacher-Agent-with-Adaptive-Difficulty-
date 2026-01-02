"""Test Wikipedia URL generation"""
topics = ['Machine Learning', 'Neural Networks', 'Deep Learning', 'Natural Language Processing']

print("Wikipedia URL Generation Test:")
print("=" * 60)
for topic in topics:
    wiki_topic = topic.replace(' ', '_')
    wiki_url = f"https://en.wikipedia.org/wiki/{wiki_topic}"
    print(f"Topic: {topic:30} -> {wiki_url}")

