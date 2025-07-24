import requests
import json
import sys

def test_api_response():
    """Test the API response format to ensure it includes the new data fields."""
    # Base URL for the API
    base_url = "http://localhost:8000"
    
    # Test cases with different input types
    test_cases = [
        {"query": "你好", "description": "Chinese input"},
        {"query": "ni3hao3", "description": "Pinyin input"},
        {"query": "hello", "description": "English input"}
    ]
    
    for test_case in test_cases:
        query = test_case["query"]
        description = test_case["description"]
        
        print(f"\nTesting {description} with query: {query}")
        
        # Make the API request
        response = requests.get(f"{base_url}/lookup", params={"text": query})
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error: Request failed with status code {response.status_code}")
            print(response.text)
            continue
        
        # Parse the response
        data = response.json()
        
        # Check if there are any results
        if not data.get("results"):
            print(f"No results found for query: {query}")
            continue
        
        # Get the first result for inspection
        first_result = data["results"][0]
        
        # Check for the new fields
        print("Checking for new fields in the response:")
        
        # Check for radical
        if "radical" in first_result:
            print(f"✓ Radical: {first_result['radical']}")
        else:
            print("✗ Radical field is missing")
        
        # Check for HSK levels
        if isinstance(first_result.get("hsk_level"), dict):
            print(f"✓ HSK levels: {first_result['hsk_level']}")
        else:
            print("✗ HSK levels are not formatted as a dictionary")
        
        # Check for parts of speech
        if "parts_of_speech" in first_result:
            print(f"✓ Parts of speech: {first_result['parts_of_speech']}")
        else:
            print("✗ Parts of speech field is missing")
        
        # Check for classifiers
        if "classifiers" in first_result:
            print(f"✓ Classifiers: {first_result['classifiers']}")
        else:
            print("✗ Classifiers field is missing")
        
        # Check for transcriptions
        if "transcriptions" in first_result:
            print(f"✓ Transcriptions: {first_result['transcriptions']}")
        else:
            print("✗ Transcriptions field is missing")
        
        # Check for meanings
        if "meanings" in first_result:
            print(f"✓ Meanings: {first_result['meanings']}")
        else:
            print("✗ Meanings field is missing")
        
        # Print the full response for the first result
        print("\nFull response for the first result:")
        print(json.dumps(first_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_api_response()