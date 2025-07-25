from src.db.connection import get_connection
from src.detection.input_detection import detect_input_type
from src.search.search import search_chinese, search_pinyin, search_english
from src.utils.pinyin_phrases import common_phrases_with_tones

def test_search(text, expected_type=None, check_prioritization=False):
    """
    Test the search functionality for a given text.
    
    Args:
        text (str): The text to search for
        expected_type (str, optional): The expected input type (chinese, pinyin, english)
        check_prioritization (bool): Whether to check search prioritization
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Detect input type
    input_type = detect_input_type(text)
    print(f"Input: '{text}'")
    print(f"Detected input type: {input_type}")
    
    # Verify expected type if provided
    if expected_type:
        assert input_type == expected_type, f"Expected input type '{expected_type}', got '{input_type}'"
    
    # Search based on input type
    if input_type == "chinese":
        results = search_chinese(text, cursor)
    elif input_type == "pinyin":
        results = search_pinyin(text, cursor)
    else:  # english
        results = search_english(text, cursor)
    
    # Print results
    print(f"Number of results: {len(results)}")
    if results:
        print("\nTop 3 results:")
        for i, result in enumerate(results[:3]):
            # Print the first result to see its structure
            if i == 0:
                print("Result structure:", result.keys())
                
                # Check prioritization if requested
                if check_prioritization and 'relevance_score' in result:
                    print(f"Relevance score: {result['relevance_score']}")
                    print(f"Match type: {result.get('match_type', 'N/A')}")
            
            # Access fields safely
            simplified = result.get('simplified', 'N/A')
            pinyin = result.get('pinyin', 'N/A')
            
            # Handle different field names for definitions
            definitions = result.get('english_definitions', result.get('definitions', 'N/A'))
            if isinstance(definitions, list):
                definitions = ', '.join(definitions)
            
            # Truncate definitions if too long
            if len(str(definitions)) > 100:
                definitions = str(definitions)[:100] + "..."
            
            print(f"{i+1}. {simplified} ({pinyin}) - {definitions}")
    else:
        print("No results found.")
    
    print("-" * 50)
    
    return results

def test_pinyin_list_implementation():
    """Test the pinyin_list implementation for syllable detection and search."""
    print("\n=== TESTING PINYIN LIST IMPLEMENTATION ===\n")
    
    # Test single syllables from pinyin_list
    single_syllables = ["ni", "hao", "wo", "shi", "ma"]
    for syllable in single_syllables:
        test_search(syllable, expected_type="pinyin")
    
    # Test compound syllables that should be detected as pinyin
    compound_syllables = ["zhong", "jiang", "xiang", "chang", "shuang"]
    for syllable in compound_syllables:
        test_search(syllable, expected_type="pinyin")
    
    # Test edge cases that could be ambiguous
    edge_cases = ["can", "fan", "man", "pen"]  # These are both valid English words and pinyin syllables
    for word in edge_cases:
        result = test_search(word)
        # These should be detected as English based on the prioritization rules
        # but should still return results

def test_common_phrases():
    """Test search functionality for common phrases with and without tones."""
    print("\n=== TESTING COMMON PHRASES ===\n")
    
    # Test a selection of common phrases without tones
    phrases_without_tones = [
        "nihao",      # hello
        "xiexie",     # thank you
        "zaijian",    # goodbye
        "duoshao",    # how much
        "woaini"      # I love you
    ]
    
    for phrase in phrases_without_tones:
        test_search(phrase, expected_type="pinyin")
    
    # Test the same phrases with tones
    phrases_with_tones = [
        "ni3hao3",      # hello
        "xie4xie5",     # thank you
        "zai4jian4",    # goodbye
        "duo1shao3",    # how much
        "wo3ai4ni3"     # I love you
    ]
    
    for phrase in phrases_with_tones:
        test_search(phrase, expected_type="pinyin")
    
    # Test phrases with spaces and tones
    phrases_with_spaces_and_tones = [
        "ni3 hao3",      # hello
        "xie4 xie5",     # thank you
        "zai4 jian4",    # goodbye
        "duo1 shao3",    # how much
        "wo3 ai4 ni3"    # I love you
    ]
    
    for phrase in phrases_with_spaces_and_tones:
        test_search(phrase, expected_type="pinyin")

def test_search_prioritization():
    """Test the search prioritization mechanism."""
    print("\n=== TESTING SEARCH PRIORITIZATION ===\n")
    
    # Test exact match prioritization
    print("Testing exact match prioritization:")
    test_search("ni3hao3", check_prioritization=True)  # Should prioritize exact tone match
    
    # Test tone-insensitive match prioritization
    print("Testing tone-insensitive match prioritization:")
    test_search("nihao", check_prioritization=True)  # Should use tone-insensitive match
    
    # Test partial match prioritization
    print("Testing partial match prioritization:")
    test_search("ni", check_prioritization=True)  # Should use partial match
    
    # Test prioritization with common phrases
    print("Testing prioritization with common phrases:")
    for phrase, with_tones in common_phrases_with_tones.items():
        if phrase in ["nihao", "xiexie", "zaijian"]:  # Test a few common phrases
            print(f"\nTesting phrase: {phrase} -> {with_tones}")
            # Test without tones
            test_search(phrase, check_prioritization=True)
            # Test with tones
            test_search(with_tones, check_prioritization=True)

# Run all tests
if __name__ == "__main__":
    # Original basic tests
    print("\n=== ORIGINAL BASIC TESTS ===\n")
    test_words = [
        "car",       # Original problem word
        "bus",       # Another short English word
        "book",      # Another short English word
        "shi",       # Valid pinyin syllable
        "nihao",     # Valid pinyin without tones
        "ni3hao3",   # Valid pinyin with tones
    ]
    
    for word in test_words:
        test_search(word)
    
    # Run new specialized tests
    test_pinyin_list_implementation()
    test_common_phrases()
    test_search_prioritization()