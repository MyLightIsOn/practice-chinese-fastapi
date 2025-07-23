from fastapi import FastAPI, Query, HTTPException
import sqlite3
from enum import Enum
import re
from typing import List, Dict, Any, Optional, Tuple

app = FastAPI()
conn = sqlite3.connect("cedict.db", check_same_thread=False)

# Input type detection functions
def contains_chinese(text: str) -> bool:
    """Check if the input contains Chinese characters."""
    # Check for Chinese characters using Unicode code point ranges
    for char in text:
        # CJK Unified Ideographs (Basic Chinese characters)
        if '\u4e00' <= char <= '\u9fff':
            return True
        # CJK Unified Ideographs Extension A
        if '\u3400' <= char <= '\u4dbf':
            return True
        # CJK Unified Ideographs Extension B
        if '\u20000' <= char <= '\u2a6df':
            return True
    return False

def is_pinyin(text: str) -> bool:
    """Check if the input matches pinyin patterns."""
    # Common English words that should not be detected as Pinyin
    common_english_words = ['hello', 'food', 'good', 'bad', 'the', 'and', 'for', 'with', 'from', 
                           'morning', 'evening', 'night', 'day', 'week', 'month', 'year']
    
    # If it's a common English word, it's not Pinyin
    if text.lower() in common_english_words:
        return False
    
    # If it contains multiple words, check if it looks like an English phrase
    words = text.split()
    if len(words) > 1:
        # If any word is a common English word, likely not Pinyin
        for word in words:
            if word.lower() in common_english_words:
                return False
        
        # If it has more than 3 words, likely an English phrase
        if len(words) > 3:
            return False
    
    # Basic pinyin pattern: letters possibly followed by tone numbers 1-4
    pinyin_pattern = r'^[a-zA-Z]+[1-4]?$'
    
    # First, try to match the entire string as a single pinyin syllable
    if re.match(r'^[a-zA-Z]+[1-4]?$', text):
        return True
    
    # If the text contains digits 1-4 (tone markers), it's likely pinyin
    if re.search(r'[1-4]', text):
        # Check if it's a valid pinyin pattern with tones
        # Allow for formats like "ni3hao3" without spaces
        if re.match(r'^([a-zA-Z]+[1-4])+$', text):
            return True
    
    # Check each word in the input if it contains spaces
    if words:
        return all(re.match(pinyin_pattern, word) for word in words)
    
    # For single words without tone numbers, check if it's a valid pinyin syllable
    if len(words) == 0 and not re.search(r'[1-4]', text):
        # Common pinyin syllables without tones
        common_syllables = ['zhi', 'chi', 'shi', 'ri', 'zi', 'ci', 'si', 'yi', 'wu', 'yu', 'ye', 'yue', 'yuan', 
                           'yin', 'yun', 'ying', 'wa', 'wo', 'wai', 'wei', 'wan', 'wen', 'wang', 'weng',
                           'ni', 'hao', 'ma', 'de', 'le', 'ba', 'ge', 'ne', 'la', 'a', 'ai', 'an', 'ang',
                           'ao', 'e', 'ei', 'en', 'er', 'o', 'ou']
        
        # If it's a common pinyin syllable, it's Pinyin
        if text.lower() in common_syllables:
            return True
    
    return False

def is_english(text: str) -> bool:
    """Check if the input contains only English characters, spaces, and punctuation."""
    # If it contains Chinese characters, it's not English
    if contains_chinese(text):
        return False
    
    # Common English words that should be detected as English
    common_english_words = ['hello', 'food', 'good', 'bad', 'the', 'and', 'for', 'with', 'from', 
                           'morning', 'evening', 'night', 'day', 'week', 'month', 'year']
    
    # If it's a common English word, it's English
    if text.lower() in common_english_words:
        return True
    
    # If it contains multiple words, check if it looks like an English phrase
    words = text.split()
    if len(words) > 1:
        # If any word is a common English word, likely English
        for word in words:
            if word.lower() in common_english_words:
                return True
        
        # If it has more than 3 words, likely an English phrase
        if len(words) > 3:
            return True
    
    # Check if the text contains only English letters, spaces, and common punctuation
    if re.match(r'^[a-zA-Z\s.,;:!?\'"-]+$', text):
        # For single words, check additional criteria
        if len(words) == 1 and len(text) > 1:
            # If it has no numbers and is longer than 3 characters, likely English
            if not re.search(r'\d', text) and len(text) > 3:
                return True
            
            # If it doesn't match typical Pinyin patterns, consider it English
            if not re.match(r'^[a-z]{1,3}[1-4]?$', text.lower()):
                return True
        else:
            # Multiple words are more likely to be English than Pinyin
            return True
    
    # If it's not Chinese and not Pinyin, we'll consider it English
    return not is_pinyin(text)

def detect_input_type(text: str) -> str:
    """Detect the type of input: Chinese, Pinyin, or English."""
    if contains_chinese(text):
        return "chinese"
    elif is_pinyin(text):
        return "pinyin"
    else:
        return "english"

def remove_tone_numbers(pinyin: str) -> str:
    """Remove tone numbers from pinyin."""
    return re.sub(r'[1-4]', '', pinyin)

# Search functions for different input types
def search_chinese(text: str, cursor, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Search for Chinese characters with priority:
    1. Exact matches in simplified/traditional
    2. Partial matches if no exact matches found
    """
    # First try exact matches
    query = """
        SELECT id, simplified, traditional, pinyin, english_definitions, 
               hsk_level, frequency_rank, 
               'exact' as match_type,
               1 as relevance_score
        FROM dictionaryentry 
        WHERE simplified = ? OR traditional = ?
        ORDER BY 
            CASE 
                WHEN hsk_level IS NULL THEN 999 
                ELSE hsk_level 
            END ASC,
            CASE 
                WHEN frequency_rank IS NULL THEN 999999 
                ELSE frequency_rank 
            END ASC
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, (text, text, limit, offset))
    results = cursor.fetchall()
    
    # If no exact matches, try partial matches
    if not results:
        query = """
            SELECT id, simplified, traditional, pinyin, english_definitions, 
                   hsk_level, frequency_rank, 
                   'partial' as match_type,
                   0.5 as relevance_score
            FROM dictionaryentry 
            WHERE simplified LIKE ? OR traditional LIKE ?
            ORDER BY 
                CASE 
                    WHEN hsk_level IS NULL THEN 999 
                    ELSE hsk_level 
                END ASC,
                CASE 
                    WHEN frequency_rank IS NULL THEN 999999 
                    ELSE frequency_rank 
                END ASC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (f"%{text}%", f"%{text}%", limit, offset))
        results = cursor.fetchall()
    
    return format_results(results)

def preprocess_pinyin(text: str) -> List[str]:
    """
    Preprocess pinyin input to handle different formats:
    - With spaces: "ni3 hao3"
    - Without spaces: "ni3hao3"
    - Without tones: "nihao"
    
    Returns a list of possible pinyin formats to search for.
    """
    variants = []
    
    # Original input
    variants.append(text)
    
    # If input has no spaces but has numbers, try to add spaces before each tone number
    if ' ' not in text and re.search(r'[1-4]', text):
        # Insert a space before each tone number
        spaced_text = re.sub(r'([a-zA-Z]+)([1-4])', r'\1\2 ', text).strip()
        variants.append(spaced_text)
        
        # Also try without tones
        variants.append(remove_tone_numbers(spaced_text))
    
    # If input has no spaces and no numbers, try common syllable breaks
    if ' ' not in text and not re.search(r'[1-4]', text):
        # Common pinyin syllables
        syllables = ['zhi', 'chi', 'shi', 'ri', 'zi', 'ci', 'si', 'yi', 'wu', 'yu', 'ye', 'yue', 'yuan', 
                    'yin', 'yun', 'ying', 'wa', 'wo', 'wai', 'wei', 'wan', 'wen', 'wang', 'weng']
        
        # Try to break the text into syllables
        for syllable in sorted(syllables, key=len, reverse=True):
            if text.startswith(syllable):
                rest = text[len(syllable):]
                if rest:
                    variants.append(f"{syllable} {rest}")
        
        # For common combinations like "nihao", add specific variants
        common_combinations = {
            "nihao": "ni3 hao3",
            "zaoan": "zao3 an1",
            "xiexie": "xie4 xie5",
            "duoshao": "duo1 shao3",
            "bukeqi": "bu4 ke4 qi5",
            "meiguanxi": "mei2 guan1 xi5",
            "zaijian": "zai4 jian4",
            "mingbai": "ming2 bai5",
            "zhidao": "zhi1 dao5",
            "xiangxin": "xiang1 xin4"
        }
        
        if text.lower() in common_combinations:
            variants.append(common_combinations[text.lower()])
    
    # If input has spaces, also try without spaces
    if ' ' in text:
        variants.append(text.replace(' ', ''))
    
    # Remove duplicates
    return list(dict.fromkeys(variants))

def search_pinyin(text: str, cursor, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Search for Pinyin with priority:
    1. Exact pinyin match (with tones)
    2. Tone-insensitive match (remove tone numbers)
    3. Partial pinyin match
    """
    all_results = []
    
    # Preprocess the pinyin input to handle different formats
    pinyin_variants = preprocess_pinyin(text)
    
    # Try each variant in order
    for variant in pinyin_variants:
        # First try exact pinyin match (with tones)
        query = """
            SELECT id, simplified, traditional, pinyin, english_definitions, 
                   hsk_level, frequency_rank, 
                   'exact_tone' as match_type,
                   1 as relevance_score
            FROM dictionaryentry 
            WHERE pinyin = ?
            ORDER BY 
                CASE 
                    WHEN hsk_level IS NULL THEN 999 
                    ELSE hsk_level 
                END ASC,
                CASE 
                    WHEN frequency_rank IS NULL THEN 999999 
                    ELSE frequency_rank 
                END ASC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (variant, limit, offset))
        results = cursor.fetchall()
        
        if results:
            return format_results(results)
    
    # If no exact matches with any variant, try tone-insensitive match
    for variant in pinyin_variants:
        # Remove tone numbers from the search text
        tone_insensitive_text = remove_tone_numbers(variant)
        
        query = """
            SELECT id, simplified, traditional, pinyin, english_definitions, 
                   hsk_level, frequency_rank, 
                   'tone_insensitive' as match_type,
                   0.8 as relevance_score
            FROM dictionaryentry 
            WHERE pinyin LIKE ? || '%'
            ORDER BY 
                CASE 
                    WHEN hsk_level IS NULL THEN 999 
                    ELSE hsk_level 
                END ASC,
                CASE 
                    WHEN frequency_rank IS NULL THEN 999999 
                    ELSE frequency_rank 
                END ASC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (tone_insensitive_text, limit, offset))
        results = cursor.fetchall()
        
        if results:
            return format_results(results)
    
    # If still no matches, try partial pinyin match
    query = """
        SELECT id, simplified, traditional, pinyin, english_definitions, 
               hsk_level, frequency_rank, 
               'partial' as match_type,
               0.5 as relevance_score
        FROM dictionaryentry 
        WHERE pinyin LIKE ?
        ORDER BY 
            CASE 
                WHEN hsk_level IS NULL THEN 999 
                ELSE hsk_level 
            END ASC,
            CASE 
                WHEN frequency_rank IS NULL THEN 999999 
                ELSE frequency_rank 
            END ASC
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, (f"%{text}%", limit, offset))
    results = cursor.fetchall()
    
    return format_results(results)

def search_english(text: str, cursor, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Search for English text using FTS and rank by:
    1. FTS match quality score
    2. HSK level
    3. Frequency ranking
    """
    # Preprocess the English text
    # For multi-word queries, use the original text
    # For single-word queries, try both the original and with wildcards
    words = text.split()
    
    if len(words) > 1:
        # Multi-word query - use as is for better phrase matching
        fts_query = text
    else:
        # Single word query - use wildcards for better matching
        fts_query = f"{text}*"
    
    # Try exact match first
    query = """
        SELECT d.id, d.simplified, d.traditional, d.pinyin, d.english_definitions, 
               d.hsk_level, d.frequency_rank, 
               'fts_exact' as match_type,
               1 as relevance_score
        FROM dictionaryentry d
        WHERE d.english_definitions LIKE ? 
        ORDER BY 
            CASE 
                WHEN d.hsk_level IS NULL THEN 999 
                ELSE d.hsk_level 
            END ASC,
            CASE 
                WHEN d.frequency_rank IS NULL THEN 999999 
                ELSE d.frequency_rank 
            END ASC
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, (f"% {text} %", limit, offset))
    results = cursor.fetchall()
    
    # If no exact matches, try FTS
    if not results:
        query = """
            SELECT d.id, d.simplified, d.traditional, d.pinyin, d.english_definitions, 
                   d.hsk_level, d.frequency_rank, 
                   'fts' as match_type,
                   0.9 as relevance_score
            FROM dictionaryentry d
            JOIN (
                SELECT id, rank
                FROM fts_english_definitions
                WHERE content MATCH ?
                ORDER BY rank
            ) as fts ON d.id = fts.id
            ORDER BY 
                fts.rank,
                CASE 
                    WHEN d.hsk_level IS NULL THEN 999 
                    ELSE d.hsk_level 
                END ASC,
                CASE 
                    WHEN d.frequency_rank IS NULL THEN 999999 
                    ELSE d.frequency_rank 
                END ASC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (fts_query, limit, offset))
        results = cursor.fetchall()
    
    # If still no results, try a more relaxed LIKE search
    if not results:
        query = """
            SELECT d.id, d.simplified, d.traditional, d.pinyin, d.english_definitions, 
                   d.hsk_level, d.frequency_rank, 
                   'partial' as match_type,
                   0.5 as relevance_score
            FROM dictionaryentry d
            WHERE d.english_definitions LIKE ? 
            ORDER BY 
                CASE 
                    WHEN d.hsk_level IS NULL THEN 999 
                    ELSE d.hsk_level 
                END ASC,
                CASE 
                    WHEN d.frequency_rank IS NULL THEN 999999 
                    ELSE d.frequency_rank 
                END ASC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (f"%{text}%", limit, offset))
        results = cursor.fetchall()
    
    return format_results(results)

def format_results(results: List[Tuple]) -> List[Dict[str, Any]]:
    """Format the database results into a list of dictionaries."""
    formatted_results = []
    for row in results:
        formatted_results.append({
            "id": row[0],
            "simplified": row[1],
            "traditional": row[2],
            "pinyin": row[3],
            "definition": row[4],
            "hsk_level": row[5],
            "frequency_rank": row[6],
            "match_type": row[7],
            "relevance_score": row[8]
        })
    return formatted_results

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

class MatchType(str, Enum):
    EXACT = "exact"
    CONTAINS = "contains"

@app.get("/lookup")
def lookup(
    text: str = Query(..., min_length=1),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    page_size: int = Query(20, ge=1, le=100, description="Number of results per page")
):
    """
    Lookup Chinese words based on the input text.
    
    The input type is automatically detected:
    - Chinese characters: Search in simplified/traditional
    - Pinyin: Search in pinyin field
    - English: Search in definitions using FTS
    
    Results are ranked based on the input type and include a match_type and relevance_score.
    """
    if not text:
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty")
    
    cursor = conn.cursor()
    
    # Calculate offset for pagination
    offset = (page - 1) * page_size
    
    # Detect input type
    input_type = detect_input_type(text)
    
    # Search based on input type
    if input_type == "chinese":
        results = search_chinese(text, cursor, limit=page_size, offset=offset)
    elif input_type == "pinyin":
        results = search_pinyin(text, cursor, limit=page_size, offset=offset)
    else:  # english
        results = search_english(text, cursor, limit=page_size, offset=offset)
    
    # Get total count for pagination info
    if input_type == "chinese":
        cursor.execute(
            "SELECT COUNT(*) FROM dictionaryentry WHERE simplified LIKE ? OR traditional LIKE ?", 
            (f"%{text}%", f"%{text}%")
        )
    elif input_type == "pinyin":
        cursor.execute(
            "SELECT COUNT(*) FROM dictionaryentry WHERE pinyin LIKE ?", 
            (f"%{text}%",)
        )
    else:  # english
        cursor.execute(
            """
            SELECT COUNT(*) FROM dictionaryentry d
            JOIN fts_english_definitions fts ON d.id = fts.id
            WHERE fts.content MATCH ?
            """, 
            (text,)
        )
    
    total_count = cursor.fetchone()[0]
    total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
    
    return {
        "input_type": input_type,
        "results": results,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages
        }
    }