import requests
import json

def test_api_health(api_url="http://localhost:8080"):
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            print("✅ API health check passed")
            return True
        else:
            print(f"API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Cannot connect to API: {e}")
        return False

def test_text_upload(api_url="http://localhost:8080"):
    test_data = {
        "text": "This is a test note from the Android app. It contains some handwritten content about biology.",
        "fileName": "test_notes.txt",
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    try:
        response = requests.post(f"{api_url}/api/upload-text", json=test_data)
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Text upload test passed")
                return True
            else:
                print(f" Text upload test failed: {result['message']}")
                return False
        else:
            print(f" Text upload test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f" Text upload test error: {e}")
        return False

def test_notes_completion(api_url="http://localhost:8080"):
    test_data = {
        "extractedText": "Photosynthesis - plants use sunlight to make food. Chlorophyll important. CO2 + H2O -> glucose + O2",
        "subject": "Biology"
    }
    
    try:
        response = requests.post(f"{api_url}/api/complete-notes", json=test_data)
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Notes completion test passed")
                print(f"   Completed notes length: {len(result['completedNotes'])} characters")
                return True
            else:
                print(f" Notes completion test failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f" Notes completion test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f" Notes completion test error: {e}")
        return False

def test_literature_upload(api_url="http://localhost:8080"):
    test_data = {
        "text": "Photosynthesis is the process by which plants convert light energy into chemical energy. The process occurs in two main stages: light-dependent reactions and light-independent reactions (Calvin cycle).",
        "title": "Introduction to Photosynthesis",
        "author": "Test Author",
        "subject": "Biology"
    }
    
    try:
        response = requests.post(f"{api_url}/api/add-literature", json=test_data)
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Literature upload test passed")
                print(f"   Document ID: {result['documentId']}")
                return True
            else:
                print(f" Literature upload test failed: {result['message']}")
                return False
        else:
            print(f" Literature upload test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f" Literature upload test error: {e}")
        return False

def test_literature_search(api_url="http://localhost:8080"):
    test_data = {
        "query": "photosynthesis chlorophyll",
        "n_results": 3
    }
    
    try:
        response = requests.post(f"{api_url}/api/search-literature", json=test_data)
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("Literature search test passed")
                print(f"   Found {result['count']} results")
                return True
            else:
                print(f" Literature search test failed: {result['message']}")
                return False
        else:
            print(f" Literature search test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f" Literature search test error: {e}")
        return False

def main():
    print(" Testing Student Notes AI System API")
    print("=" * 50)
    
    api_url = "http://localhost:8080"
    tests = [
        ("API Health Check", test_api_health),
        ("Text Upload", test_text_upload),
        ("Literature Upload", test_literature_upload),
        ("Literature Search", test_literature_search),
        ("Notes Completion", test_notes_completion),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n🔧 Running {test_name}...")
        if test_func(api_url):
            passed += 1
    
    print("\\n" + "=" * 50)
    print(f" Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(" All tests passed! The system is ready.")
    else:
        print(" Some tests failed. Check the server logs for details.")

if __name__ == '__main__':
    main()
