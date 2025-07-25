import re
from typing import List, Dict, Any
from src.detection.input_detection import remove_tone_numbers, pinyin_list
from src.db.connection import format_results
from src.utils.pinyin_phrases import common_phrases_with_tones

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
        # Use the comprehensive pinyin_list instead of hardcoded syllables
        # Sort by length (longest first) to prioritize longer syllables
        sorted_syllables = sorted(pinyin_list, key=len, reverse=True)

        # Try to break the text into syllables
        for syllable in sorted_syllables:
            if text.startswith(syllable):
                rest = text[len(syllable):]
                if rest:
                    variants.append(f"{syllable} {rest}")

        # Check if this is a common phrase that we know the tones for
        if text.lower() in common_phrases_with_tones:
            variants.append(common_phrases_with_tones[text.lower()])

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
    1. Direct translation match (for single words)
    2. FTS match quality score
    3. HSK level
    4. Frequency ranking
    """
    # Preprocess the English text
    # For multi-word queries, use the original text
    # For single-word queries, try both the original and with wildcards
    words = text.split()
    is_single_word = len(words) == 1

    if not is_single_word:
        # Multi-word query - use as is for better phrase matching
        fts_query = text
    else:
        # Single word query - use wildcards for better matching
        fts_query = f"{text}*"

    all_results = []
    
    # For single word queries, prioritize direct translations
    if is_single_word:
        # First, try to find direct translations where the word appears at the beginning of the definition
        # This will prioritize entries like "car; automobile; bus" for the query "car"
        # Also match entries that start with the search term followed by a space, like "cat (CL:隻|只[zhi1])"
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
                       'direct_translation' as match_type,
                       2.0                  as relevance_score
                FROM dictionaryentry d
                WHERE d.english_definitions LIKE ? OR d.english_definitions LIKE ? OR d.english_definitions LIKE ?
                ORDER BY CASE \
                             WHEN d.hsk_level IS NULL THEN 999 \
                             ELSE d.hsk_level \
                             END ASC, \
                         CASE \
                             WHEN d.frequency_rank IS NULL THEN 999999 \
                             ELSE d.frequency_rank \
                             END ASC
                """
        cursor.execute(query, (f"{text};%", f"{text},%", f"{text} %"))
        direct_results = cursor.fetchall()
        
        if direct_results:
            all_results.extend(direct_results)

    # Try exact match next
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
                         END ASC
            """
    cursor.execute(query, (f"% {text} %",))
    exact_results = cursor.fetchall()
    if exact_results:
        all_results.extend(exact_results)

    # Try FTS
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
                         END ASC
            """
    cursor.execute(query, (fts_query,))
    fts_results = cursor.fetchall()
    if fts_results:
        all_results.extend(fts_results)

    # Try a more relaxed LIKE search
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
                         END ASC
            """
    cursor.execute(query, (f"%{text}%",))
    partial_results = cursor.fetchall()
    if partial_results:
        all_results.extend(partial_results)

    # Remove duplicates based on entry ID
    seen_ids = set()
    unique_results = []
    for result in all_results:
        if result[0] not in seen_ids:  # Check if ID is already seen
            seen_ids.add(result[0])
            unique_results.append(result)

    # Apply pagination to the combined results
    paginated_results = unique_results[offset:offset + limit]

    return format_results(paginated_results)