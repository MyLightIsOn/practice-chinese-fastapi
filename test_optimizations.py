import sqlite3
import time

def test_query(query, params, description):
    """Execute a query and measure its execution time."""
    conn = sqlite3.connect("cedict.db")
    cursor = conn.cursor()
    
    start_time = time.time()
    cursor.execute(query, params)
    results = cursor.fetchall()
    end_time = time.time()
    
    print(f"\n{description}")
    print(f"Query: {query}")
    print(f"Params: {params}")
    print(f"Results count: {len(results)}")
    print(f"Execution time: {(end_time - start_time) * 1000:.2f} ms")
    
    if results:
        print("First result:")
        print(results[0])
    
    conn.close()
    return results

# Test 1: Search for simplified characters with LIKE (original approach)
test_query(
    "SELECT * FROM dictionaryentry WHERE simplified LIKE ? OR traditional LIKE ?",
    ("%你好%", "%你好%"),
    "Test 1: Original LIKE query for '你好'"
)

# Test 2: Search for simplified characters with exact match
test_query(
    "SELECT * FROM dictionaryentry WHERE simplified = ?",
    ("你好",),
    "Test 2: Exact match query for simplified '你好'"
)

# Test 3: Search for English definitions using FTS
test_query(
    """
    SELECT d.* FROM dictionaryentry d
    JOIN fts_english_definitions fts ON d.id = fts.id
    WHERE fts.content MATCH ?
    """,
    ("hello",),
    "Test 3: FTS query for English definition 'hello'"
)

# Test 4: Search for English definitions using exact match
test_query(
    """
    SELECT d.* FROM dictionaryentry d
    JOIN fts_english_definitions fts ON d.id = fts.id
    WHERE fts.content = ?
    """,
    ("hello",),
    "Test 4: Exact match query for English definition 'hello'"
)

# Test 5: Search across all fields with UNION
test_query(
    """
    SELECT * FROM dictionaryentry 
    WHERE simplified LIKE ? OR traditional LIKE ? OR pinyin LIKE ?
    UNION
    SELECT d.* FROM dictionaryentry d
    JOIN fts_english_definitions fts ON d.id = fts.id
    WHERE fts.content MATCH ?
    """,
    ("%你好%", "%你好%", "%nihao%", "hello"),
    "Test 5: Combined query across all fields for '你好' and 'hello'"
)

print("\nAll tests completed successfully!")