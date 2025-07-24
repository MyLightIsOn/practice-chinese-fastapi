from src.db.connection import get_connection
from src.detection.input_detection import detect_input_type
from src.search.search import search_chinese, search_pinyin, search_english

def test_search(text):
    """Test the search functionality for a given text."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Detect input type
    input_type = detect_input_type(text)
    print(f"Input: '{text}'")
    print(f"Detected input type: {input_type}")
    
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

# Test with various inputs
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