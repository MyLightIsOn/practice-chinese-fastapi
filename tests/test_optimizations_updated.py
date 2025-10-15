import sqlite3
import time

def test_query(query, params, description):
    """Execute a query and measure its execution time."""
    conn = sqlite3.connect("../archive/cedict.db")
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

# Original Tests

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

# New Tests for Enhanced Schema

# Test 6: Search by radical
test_query(
    "SELECT * FROM dictionaryentry WHERE radical = ?",
    ("扌",),
    "Test 6: Search by radical '扌'"
)

# Test 7: Search by HSK level (old system)
test_query(
    "SELECT * FROM dictionaryentry WHERE old_hsk_level = ?",
    (3,),
    "Test 7: Search by old HSK level 3"
)

# Test 8: Search by HSK level (new system)
test_query(
    "SELECT * FROM dictionaryentry WHERE new_hsk_level = ?",
    (4,),
    "Test 8: Search by new HSK level 4"
)

# Test 9: Search by part of speech
test_query(
    """
    SELECT d.* FROM dictionaryentry d
    JOIN part_of_speech pos ON d.id = pos.entry_id
    WHERE pos.pos = ?
    """,
    ("v",),
    "Test 9: Search by part of speech 'v' (verb)"
)

# Test 10: Search by classifier
test_query(
    """
    SELECT d.* FROM dictionaryentry d
    JOIN classifier c ON d.id = c.entry_id
    WHERE c.classifier = ?
    """,
    ("个",),
    "Test 10: Search by classifier '个'"
)

# Test 11: Search by transcription system
test_query(
    """
    SELECT d.* FROM dictionaryentry d
    JOIN transcription t ON d.id = t.entry_id
    WHERE t.system = ? AND t.value LIKE ?
    """,
    ("wadegiles", "%chao%"),
    "Test 11: Search by Wade-Giles transcription containing 'chao'"
)

# Test 12: Search by meaning
test_query(
    """
    SELECT d.* FROM dictionaryentry d
    JOIN meaning m ON d.id = m.entry_id
    WHERE m.definition LIKE ?
    """,
    ("%hello%",),
    "Test 12: Search by meaning containing 'hello'"
)

# Test 13: Complex query joining multiple tables
test_query(
    """
    SELECT d.* FROM dictionaryentry d
    JOIN part_of_speech pos ON d.id = pos.entry_id
    JOIN transcription t ON d.id = t.entry_id
    WHERE pos.pos = ? AND t.system = ? AND d.new_hsk_level <= ?
    """,
    ("n", "pinyin", 3),
    "Test 13: Complex query for nouns with pinyin transcription and HSK level <= 3"
)

# Test 14: Performance test for large result set
test_query(
    """
    SELECT d.*, pos.pos, c.classifier, t.system, t.value, m.definition
    FROM dictionaryentry d
    LEFT JOIN part_of_speech pos ON d.id = pos.entry_id
    LEFT JOIN classifier c ON d.id = c.entry_id
    LEFT JOIN transcription t ON d.id = t.entry_id AND t.system = 'pinyin'
    LEFT JOIN meaning m ON d.id = m.entry_id
    WHERE d.hsk_level IS NOT NULL
    LIMIT 100
    """,
    (),
    "Test 14: Performance test for joining all tables with HSK words (limited to 100 results)"
)

print("\nAll tests completed successfully!")

# Performance Analysis and Recommendations
print("\n=== Performance Analysis and Recommendations ===")
print("""
Based on the test results, here are some recommendations for optimizing performance:

1. Consider adding composite indexes for frequently used query patterns:
   - CREATE INDEX idx_hsk_radical ON dictionaryentry(new_hsk_level, radical);
   - CREATE INDEX idx_pos_system ON part_of_speech(pos), transcription(system);

2. For complex joins across multiple tables, consider creating views for common query patterns.

3. For large result sets, ensure pagination is used consistently.

4. Monitor query performance in production and adjust indexes based on actual usage patterns.

5. Consider adding full-text search capabilities to the meaning table for more efficient text searches.
""")