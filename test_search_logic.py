import sys
import json
from typing import Dict, Any

# Import functions directly from source modules
sys.path.append('.')
from src.api.endpoints import lookup
from src.detection.input_detection import detect_input_type

def test_search(text: str, description: str):
    """Test the lookup function with the given text and print the results."""
    print(f"\n=== Testing: {description} ===")
    print(f"Input: '{text}'")
    
    # Detect input type
    input_type = detect_input_type(text)
    print(f"Detected input type: {input_type}")
    
    # Call the lookup function directly with actual values
    result = lookup(text=text, page=1, page_size=20)
    
    # Print the results
    pagination = result['pagination']
    print(f"Pagination: Page {pagination['page']} of {pagination['total_pages']} " +
          f"(Total results: {pagination['total_count']})")
    
    results = result['results']
    print(f"Results count: {len(results)}")
    
    if results:
        print("\nFirst 3 results:")
        for i, result in enumerate(results[:3]):
            print(f"{i+1}. {result['simplified']} ({result['traditional']}) - {result['pinyin']}")
            print(f"   Definition: {result['definition'][:100]}...")
            print(f"   Match type: {result['match_type']}, Relevance: {result['relevance_score']}")
            print(f"   HSK Level: {result['hsk_level']}, Frequency Rank: {result['frequency_rank']}")
            print()

def main():
    """Run tests for different input types."""
    # Test Chinese input
    test_search("你好", "Chinese characters (exact match)")
    test_search("中", "Chinese character (partial match)")
    
    # Test Pinyin input
    test_search("ni3hao3", "Pinyin with tones (exact match)")
    test_search("nihao", "Pinyin without tones (tone-insensitive match)")
    test_search("zh", "Pinyin prefix (partial match)")
    
    # Test English input
    test_search("hello", "English word (FTS match)")
    test_search("food", "English word (FTS match)")
    
    # Test edge cases
    test_search("中国", "Multiple Chinese characters")
    test_search("ni3 hao3", "Multiple Pinyin syllables with spaces")
    test_search("good morning", "Multiple English words")

if __name__ == "__main__":
    main()