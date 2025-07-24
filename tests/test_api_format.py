import sqlite3
import json
import sys
from src.search.search import search_chinese, search_pinyin, search_english

def test_search_function(search_func, query, description):
    """Test a search function with a sample query."""
    conn = sqlite3.connect("../cedict.db")
    cursor = conn.cursor()
    
    print(f"\nTesting {description} for query: '{query}'")
    
    results = search_func(query, cursor)
    
    if results:
        # Print the first result in a formatted way
        result = results[0]
        print("\nFirst result:")
        print(f"  Simplified: {result['simplified']}")
        print(f"  Traditional: {result['traditional']}")
        print(f"  Pinyin: {result['pinyin']}")
        
        # Print HSK information
        print("\n  HSK Information:")
        if 'hsk' in result:
            hsk = result['hsk']
            if 'old' in hsk:
                print(f"    Old HSK Level: {hsk['old']}")
            if 'new' in hsk:
                print(f"    New HSK Level: {hsk['new']}")
            print(f"    Combined HSK Level: {hsk['combined']}")
        else:
            print("    No HSK information available")
        
        # Print radical information
        if 'radical' in result and result['radical']:
            print(f"\n  Radical: {result['radical']}")
        
        # Print parts of speech
        if 'parts_of_speech' in result and result['parts_of_speech']:
            print("\n  Parts of Speech:")
            for pos in result['parts_of_speech']:
                print(f"    - {pos}")
        
        # Print classifiers
        if 'classifiers' in result and result['classifiers']:
            print("\n  Classifiers:")
            for classifier in result['classifiers']:
                print(f"    - {classifier}")
        
        # Print transcriptions
        if 'transcriptions' in result and result['transcriptions']:
            print("\n  Transcriptions:")
            for system, value in result['transcriptions'].items():
                print(f"    {system}: {value}")
        
        # Print meanings
        if 'meanings' in result and result['meanings']:
            print("\n  Meanings:")
            for meaning in result['meanings']:
                print(f"    - {meaning}")
        
        # Print original definition for comparison
        print(f"\n  Original Definition: {result['definition']}")
        
        # Print match type and relevance score
        print(f"\n  Match Type: {result['match_type']}")
        print(f"  Relevance Score: {result['relevance_score']}")
        
        # Print the full JSON for reference
        print("\nFull JSON response for first result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("No results found.")
    
    conn.close()

if __name__ == "__main__":
    # Test with different types of queries
    print("=== Testing API Response Format ===")
    
    # Test Chinese search
    test_search_function(search_chinese, "你好", "Chinese search")
    
    # Test Pinyin search
    test_search_function(search_pinyin, "nihao", "Pinyin search")
    
    # Test English search
    test_search_function(search_english, "hello", "English search")
    
    print("\nAll tests completed.")