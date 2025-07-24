#!/usr/bin/env python3
"""
Performance Optimization Script for Chinese Dictionary Database

This script implements performance optimizations for the Chinese dictionary database:
1. Creates indexes for frequently searched columns
2. Optimizes database queries
3. Implements proper transaction handling for batch operations
"""

import sqlite3
import time
import sys

def create_indexes(conn):
    """Create indexes for frequently searched columns"""
    print("Creating indexes for frequently searched columns...")
    cursor = conn.cursor()
    
    # Start a transaction for creating all indexes
    conn.execute("BEGIN TRANSACTION")
    
    try:
        # Indexes for the main dictionaryentry table
        indexes = [
            # Index for simplified and traditional columns (frequently searched in Chinese search)
            "CREATE INDEX IF NOT EXISTS idx_simplified ON dictionaryentry(simplified)",
            "CREATE INDEX IF NOT EXISTS idx_traditional ON dictionaryentry(traditional)",
            
            # Index for pinyin column (frequently searched in Pinyin search)
            "CREATE INDEX IF NOT EXISTS idx_pinyin ON dictionaryentry(pinyin)",
            
            # Indexes for sorting and filtering
            "CREATE INDEX IF NOT EXISTS idx_hsk_level ON dictionaryentry(hsk_level)",
            "CREATE INDEX IF NOT EXISTS idx_frequency_rank ON dictionaryentry(frequency_rank)",
            "CREATE INDEX IF NOT EXISTS idx_old_hsk_level ON dictionaryentry(old_hsk_level)",
            "CREATE INDEX IF NOT EXISTS idx_new_hsk_level ON dictionaryentry(new_hsk_level)",
            "CREATE INDEX IF NOT EXISTS idx_radical ON dictionaryentry(radical)",
            
            # Indexes for related tables
            "CREATE INDEX IF NOT EXISTS idx_part_of_speech_entry_id ON part_of_speech(entry_id)",
            "CREATE INDEX IF NOT EXISTS idx_classifier_entry_id ON classifier(entry_id)",
            "CREATE INDEX IF NOT EXISTS idx_transcription_entry_id ON transcription(entry_id)",
            "CREATE INDEX IF NOT EXISTS idx_meaning_entry_id ON meaning(entry_id)",
            
            # Compound indexes for common query patterns
            "CREATE INDEX IF NOT EXISTS idx_hsk_freq ON dictionaryentry(hsk_level, frequency_rank)",
        ]
        
        # Execute each index creation statement
        for index_sql in indexes:
            cursor.execute(index_sql)
            print(f"Created index: {index_sql}")
        
        # Commit the transaction
        conn.commit()
        print("All indexes created successfully.")
        
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Error creating indexes: {e}")
        raise

def analyze_database(conn):
    """Run ANALYZE to update statistics for the query planner"""
    print("Analyzing database for query optimization...")
    cursor = conn.cursor()
    cursor.execute("ANALYZE")
    print("Database analysis completed.")

def optimize_database(conn):
    """Run VACUUM to rebuild the database file and optimize storage"""
    print("Optimizing database storage...")
    # VACUUM requires its own connection with specific pragmas
    conn.execute("PRAGMA auto_vacuum = FULL")
    conn.execute("VACUUM")
    print("Database storage optimization completed.")

def test_query_performance(conn, query, params=(), iterations=5):
    """Test the performance of a query"""
    cursor = conn.cursor()
    total_time = 0
    
    for i in range(iterations):
        start_time = time.time()
        cursor.execute(query, params)
        results = cursor.fetchall()
        end_time = time.time()
        
        execution_time = end_time - start_time
        total_time += execution_time
        print(f"  Iteration {i+1}: {execution_time:.4f} seconds, {len(results)} results")
    
    avg_time = total_time / iterations
    print(f"  Average execution time: {avg_time:.4f} seconds")
    return avg_time

def run_performance_tests(conn):
    """Run performance tests on common queries"""
    print("\nRunning performance tests on common queries...")
    
    # Test Chinese search
    print("\nTesting Chinese search query:")
    chinese_query = """
    SELECT d.id, d.simplified, d.traditional, d.pinyin, d.english_definitions,
           d.hsk_level, d.frequency_rank, d.radical, d.old_hsk_level, d.new_hsk_level,
           'exact' as match_type, 1 as relevance_score
    FROM dictionaryentry d
    WHERE d.simplified = ? OR d.traditional = ?
    ORDER BY CASE WHEN d.hsk_level IS NULL THEN 999 ELSE d.hsk_level END ASC,
             CASE WHEN d.frequency_rank IS NULL THEN 999999 ELSE d.frequency_rank END ASC
    LIMIT 20
    """
    test_query_performance(conn, chinese_query, ("你好", "你好"))
    
    # Test Pinyin search
    print("\nTesting Pinyin search query:")
    pinyin_query = """
    SELECT d.id, d.simplified, d.traditional, d.pinyin, d.english_definitions,
           d.hsk_level, d.frequency_rank, d.radical, d.old_hsk_level, d.new_hsk_level,
           'exact_tone' as match_type, 1 as relevance_score
    FROM dictionaryentry d
    WHERE d.pinyin = ?
    ORDER BY CASE WHEN d.hsk_level IS NULL THEN 999 ELSE d.hsk_level END ASC,
             CASE WHEN d.frequency_rank IS NULL THEN 999999 ELSE d.frequency_rank END ASC
    LIMIT 20
    """
    test_query_performance(conn, pinyin_query, ("ni3 hao3",))
    
    # Test English search
    print("\nTesting English search query:")
    english_query = """
    SELECT d.id, d.simplified, d.traditional, d.pinyin, d.english_definitions,
           d.hsk_level, d.frequency_rank, d.radical, d.old_hsk_level, d.new_hsk_level,
           'fts' as match_type, 0.9 as relevance_score
    FROM dictionaryentry d
    JOIN (SELECT id, rank FROM fts_english_definitions 
          WHERE content MATCH ? ORDER BY rank) as fts ON d.id = fts.id
    ORDER BY fts.rank,
             CASE WHEN d.hsk_level IS NULL THEN 999 ELSE d.hsk_level END ASC,
             CASE WHEN d.frequency_rank IS NULL THEN 999999 ELSE d.frequency_rank END ASC
    LIMIT 20
    """
    test_query_performance(conn, english_query, ("hello",))
    
    # Test format_results performance with optimized query
    print("\nTesting optimized format_results query:")
    optimized_query = """
    SELECT d.id, d.simplified, d.traditional, d.pinyin, d.english_definitions,
           d.hsk_level, d.frequency_rank, d.radical, d.old_hsk_level, d.new_hsk_level,
           'test' as match_type, 1.0 as relevance_score,
           GROUP_CONCAT(DISTINCT pos.pos) as parts_of_speech,
           GROUP_CONCAT(DISTINCT c.classifier) as classifiers,
           GROUP_CONCAT(DISTINCT (t.system || ':' || t.value)) as transcriptions,
           GROUP_CONCAT(DISTINCT m.definition) as meanings
    FROM dictionaryentry d
    LEFT JOIN part_of_speech pos ON d.id = pos.entry_id
    LEFT JOIN classifier c ON d.id = c.entry_id
    LEFT JOIN transcription t ON d.id = t.entry_id
    LEFT JOIN meaning m ON d.id = m.entry_id
    WHERE d.simplified = ? OR d.traditional = ?
    GROUP BY d.id
    LIMIT 5
    """
    test_query_performance(conn, optimized_query, ("你好", "你好"))

def main():
    """Main function to run the performance optimizations"""
    db_path = "cedict.db"
    
    try:
        # Connect to the database
        print(f"Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Create indexes
        create_indexes(conn)
        
        # Analyze database for query optimization
        analyze_database(conn)
        
        # Run performance tests
        run_performance_tests(conn)
        
        # Optimize database storage
        optimize_database(conn)
        
        print("\nPerformance optimization completed successfully.")
        
    except Exception as e:
        print(f"Error during performance optimization: {e}")
        return 1
    finally:
        # Close the database connection
        if 'conn' in locals():
            conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())