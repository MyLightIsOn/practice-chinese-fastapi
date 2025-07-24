import re
from typing import List, Dict, Any
import sqlite3

from src.detection.input_detection import remove_tone_numbers
from src.db.connection import format_results

def search_chinese(text: str, cursor, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Search for Chinese characters with priority:
    1. Exact matches in simplified/traditional
    2. Partial matches if no exact matches found
    """
    # First try exact matches
    query = """
            SELECT d.id, \
                   d.simplified, \
                   d.traditional, \
                   d.pinyin, \
                   d.english_definitions,
                   d.hsk_level, \
                   d.frequency_rank, \
                   d.radical, \
                   d.old_hsk_level, \
                   d.new_hsk_level,
                   'exact' as match_type,
                   1       as relevance_score
            FROM dictionaryentry d
            WHERE d.simplified = ? \
               OR d.traditional = ?
            ORDER BY CASE \
                         WHEN d.hsk_level IS NULL THEN 999 \
                         ELSE d.hsk_level \
                         END ASC, \
                     CASE \
                         WHEN d.frequency_rank IS NULL THEN 999999 \
                         ELSE d.frequency_rank \
                         END ASC LIMIT ? \
            OFFSET ? \
            """
    cursor.execute(query, (text, text, limit, offset))
    results = cursor.fetchall()

    # If no exact matches, try partial matches
    if not results:
        query = """
                SELECT d.id, \
                       d.simplified, \
                       d.traditional, \
                       d.pinyin, \
                       d.english_definitions,
                       d.hsk_level, \
                       d.frequency_rank, \
                       d.radical, \
                       d.old_hsk_level, \
                       d.new_hsk_level,
                       'partial' as match_type,
                       0.5       as relevance_score
                FROM dictionaryentry d
                WHERE d.simplified LIKE ? \
                   OR d.traditional LIKE ?
                ORDER BY CASE \
                             WHEN d.hsk_level IS NULL THEN 999 \
                             ELSE d.hsk_level \
                             END ASC, \
                         CASE \
                             WHEN d.frequency_rank IS NULL THEN 999999 \
                             ELSE d.frequency_rank \
                             END ASC LIMIT ? \
                OFFSET ? \
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
                SELECT d.id, \
                       d.simplified, \
                       d.traditional, \
                       d.pinyin, \
                       d.english_definitions,
                       d.hsk_level, \
                       d.frequency_rank, \
                       d.radical, \
                       d.old_hsk_level, \
                       d.new_hsk_level,
                       'exact_tone' as match_type,
                       1            as relevance_score
                FROM dictionaryentry d
                WHERE d.pinyin = ?
                ORDER BY CASE \
                             WHEN d.hsk_level IS NULL THEN 999 \
                             ELSE d.hsk_level \
                             END ASC, \
                         CASE \
                             WHEN d.frequency_rank IS NULL THEN 999999 \
                             ELSE d.frequency_rank \
                             END ASC LIMIT ? \
                OFFSET ? \
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
                SELECT d.id, \
                       d.simplified, \
                       d.traditional, \
                       d.pinyin, \
                       d.english_definitions,
                       d.hsk_level, \
                       d.frequency_rank, \
                       d.radical, \
                       d.old_hsk_level, \
                       d.new_hsk_level,
                       'tone_insensitive' as match_type,
                       0.8                as relevance_score
                FROM dictionaryentry d
                WHERE d.pinyin LIKE ? || '%'
                ORDER BY CASE \
                             WHEN d.hsk_level IS NULL THEN 999 \
                             ELSE d.hsk_level \
                             END ASC, \
                         CASE \
                             WHEN d.frequency_rank IS NULL THEN 999999 \
                             ELSE d.frequency_rank \
                             END ASC LIMIT ? \
                OFFSET ? \
                """
        cursor.execute(query, (tone_insensitive_text, limit, offset))
        results = cursor.fetchall()

        if results:
            return format_results(results)

    # If still no matches, try partial pinyin match
    query = """
            SELECT d.id, \
                   d.simplified, \
                   d.traditional, \
                   d.pinyin, \
                   d.english_definitions,
                   d.hsk_level, \
                   d.frequency_rank, \
                   d.radical, \
                   d.old_hsk_level, \
                   d.new_hsk_level,
                   'partial' as match_type,
                   0.5       as relevance_score
            FROM dictionaryentry d
            WHERE d.pinyin LIKE ?
            ORDER BY CASE \
                         WHEN d.hsk_level IS NULL THEN 999 \
                         ELSE d.hsk_level \
                         END ASC, \
                     CASE \
                         WHEN d.frequency_rank IS NULL THEN 999999 \
                         ELSE d.frequency_rank \
                         END ASC LIMIT ? \
            OFFSET ? \
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
            SELECT d.id, \
                   d.simplified, \
                   d.traditional, \
                   d.pinyin, \
                   d.english_definitions,
                   d.hsk_level, \
                   d.frequency_rank, \
                   d.radical, \
                   d.old_hsk_level, \
                   d.new_hsk_level,
                   'fts_exact' as match_type,
                   1           as relevance_score
            FROM dictionaryentry d
            WHERE d.english_definitions LIKE ?
            ORDER BY CASE \
                         WHEN d.hsk_level IS NULL THEN 999 \
                         ELSE d.hsk_level \
                         END ASC, \
                     CASE \
                         WHEN d.frequency_rank IS NULL THEN 999999 \
                         ELSE d.frequency_rank \
                         END ASC LIMIT ? \
            OFFSET ? \
            """
    cursor.execute(query, (f"% {text} %", limit, offset))
    results = cursor.fetchall()

    # If no exact matches, try FTS
    if not results:
        query = """
                SELECT d.id, \
                       d.simplified, \
                       d.traditional, \
                       d.pinyin, \
                       d.english_definitions,
                       d.hsk_level, \
                       d.frequency_rank, \
                       d.radical, \
                       d.old_hsk_level, \
                       d.new_hsk_level,
                       'fts' as match_type,
                       0.9   as relevance_score
                FROM dictionaryentry d
                         JOIN (SELECT id, rank \
                               FROM fts_english_definitions \
                               WHERE content MATCH ? \
                               ORDER BY rank) as fts ON d.id = fts.id
                ORDER BY fts.rank, \
                         CASE \
                             WHEN d.hsk_level IS NULL THEN 999 \
                             ELSE d.hsk_level \
                             END ASC, \
                         CASE \
                             WHEN d.frequency_rank IS NULL THEN 999999 \
                             ELSE d.frequency_rank \
                             END ASC LIMIT ? \
                OFFSET ? \
                """
        cursor.execute(query, (fts_query, limit, offset))
        results = cursor.fetchall()

    # If still no results, try a more relaxed LIKE search
    if not results:
        query = """
                SELECT d.id, \
                       d.simplified, \
                       d.traditional, \
                       d.pinyin, \
                       d.english_definitions,
                       d.hsk_level, \
                       d.frequency_rank, \
                       d.radical, \
                       d.old_hsk_level, \
                       d.new_hsk_level,
                       'partial' as match_type,
                       0.5       as relevance_score
                FROM dictionaryentry d
                WHERE d.english_definitions LIKE ?
                ORDER BY CASE \
                             WHEN d.hsk_level IS NULL THEN 999 \
                             ELSE d.hsk_level \
                             END ASC, \
                         CASE \
                             WHEN d.frequency_rank IS NULL THEN 999999 \
                             ELSE d.frequency_rank \
                             END ASC LIMIT ? \
                OFFSET ? \
                """
        cursor.execute(query, (f"%{text}%", limit, offset))
        results = cursor.fetchall()

    return format_results(results)