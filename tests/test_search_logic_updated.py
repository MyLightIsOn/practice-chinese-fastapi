import sys
import json
from typing import Dict, Any

# Import functions directly from source modules
sys.path.append('..')
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
    result = lookup(text=text, page=1, page_size=100)
    
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
            
            # Check for the new fields
            print(f"   Definition: {result['definition'][:100]}...")
            print(f"   Match type: {result['match_type']}, Relevance: {result['relevance_score']}")
            
            # Check HSK level format
            if isinstance(result.get('hsk_level'), dict):
                hsk = result['hsk_level']
                print(f"   HSK Level: Old={hsk.get('old')}, New={hsk.get('new')}, Combined={hsk.get('combined')}")
            else:
                print(f"   HSK Level: {result.get('hsk_level')}")
            
            print(f"   Frequency Rank: {result.get('frequency_rank')}")
            
            # Check for radical
            if 'radical' in result:
                print(f"   Radical: {result['radical']}")
            
            # Check for parts of speech
            if 'parts_of_speech' in result:
                print(f"   Parts of Speech: {result['parts_of_speech']}")
            
            # Check for classifiers
            if 'classifiers' in result:
                print(f"   Classifiers: {result['classifiers']}")
            
            # Check for transcriptions
            if 'transcriptions' in result:
                print(f"   Transcriptions: {json.dumps(result['transcriptions'], ensure_ascii=False)}")
            
            # Check for meanings
            if 'meanings' in result:
                print(f"   Meanings: {result['meanings']}")
            
            print()
            
            # Validate the structure of the result
            validate_result_structure(result)

def validate_result_structure(result):
    """Validate the structure of a search result."""
    # Check for required fields
    required_fields = ['id', 'simplified', 'traditional', 'pinyin', 'definition']
    for field in required_fields:
        if field not in result:
            print(f"   ❌ Missing required field: {field}")
    
    # Check HSK level structure
    if isinstance(result.get('hsk_level'), dict):
        hsk = result['hsk_level']
        expected_keys = ['combined', 'old', 'new']
        for key in expected_keys:
            if key not in hsk:
                print(f"   ❌ Missing key in hsk_level: {key}")
    else:
        print("   ❌ HSK level is not formatted as a dictionary")
    
    # Check array fields
    array_fields = ['parts_of_speech', 'classifiers', 'meanings']
    for field in array_fields:
        if field in result and not isinstance(result[field], list):
            print(f"   ❌ {field} is not an array")
    
    # Check transcriptions structure
    if 'transcriptions' in result:
        if not isinstance(result['transcriptions'], dict):
            print("   ❌ transcriptions is not a dictionary")
        else:
            expected_systems = ['pinyin', 'numeric', 'wadegiles', 'bopomofo', 'romatzyh']
            for system in result['transcriptions'].keys():
                if system not in expected_systems:
                    print(f"   ⚠️ Unexpected transcription system: {system}")

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