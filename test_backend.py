"""
Simple script to test if backend is working
Run this while backend is running on http://localhost:8000
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, url, data=None):
    """Test an endpoint"""
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        print(f"\n{'='*50}")
        print(f"Testing: {name}")
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ FAILED")
            print(f"Error: {response.text}")
        
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Cannot connect to {url}")
        print("Make sure backend is running: cd src && python app.py")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def main():
    print("="*50)
    print("BACKEND TESTING SCRIPT")
    print("="*50)
    print("\nMake sure backend is running on http://localhost:8000")
    print("Start backend: cd src && python app.py\n")
    
    results = []
    
    # Test 1: Health check
    results.append(test_endpoint(
        "Health Check",
        "GET",
        f"{BASE_URL}/api/health"
    ))
    
    # Test 2: Root endpoint
    results.append(test_endpoint(
        "Root Endpoint",
        "GET",
        f"{BASE_URL}/"
    ))
    
    # Test 3: Data sources
    results.append(test_endpoint(
        "Data Sources Info",
        "GET",
        f"{BASE_URL}/api/data-sources"
    ))
    
    # Test 4: Dataset stats
    results.append(test_endpoint(
        "Dataset Statistics",
        "GET",
        f"{BASE_URL}/api/dataset/stats"
    ))
    
    # Test 5: Explain topic
    results.append(test_endpoint(
        "Explain Topic",
        "POST",
        f"{BASE_URL}/api/topics/explain",
        {"topic_name": "Python Basics"}
    ))
    
    # Test 6: Query dataset
    results.append(test_endpoint(
        "Query Dataset (Search)",
        "POST",
        f"{BASE_URL}/api/query",
        {"query_type": "search", "query": "python", "limit": 5}
    ))
    
    # Test 7: Chat
    results.append(test_endpoint(
        "Chat with Agent",
        "POST",
        f"{BASE_URL}/api/chat/message",
        {"message": "Hello, what is Python?", "user_id": "test_user"}
    ))
    
    # Test 8: Summarize
    results.append(test_endpoint(
        "Summarize Content",
        "POST",
        f"{BASE_URL}/api/reasoning/summarize",
        {"content": "Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms."}
    ))
    
    # Test 9: Classify
    results.append(test_endpoint(
        "Classify Content",
        "POST",
        f"{BASE_URL}/api/reasoning/classify",
        {"content": "How do I learn Python programming?", "categories": ["academic", "technical", "general"]}
    ))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Backend is working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Check backend logs")
    print("="*50)

if __name__ == "__main__":
    main()

