import re
from typing import List, Dict, Any
from src.detection.input_detection import remove_tone_numbers, pinyin_list
from src.db.connection import format_results
from src.utils.pinyin_phrases import common_phrases_with_tones
from supabase import Client

def search_chinese(text: str, client: Client, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Search for Chinese characters with priority:
    1. Exact matches in simplified/traditional
    2. Partial matches if no exact matches found
    """
    start = offset
    end = offset + limit - 1

    # First: exact matches
    exact = (
        client.table("dictionaryentry")
        .select("id,simplified,traditional,pinyin,english_definitions,hsk_level,frequency_rank,radical,old_hsk_level,new_hsk_level")
        .or_(f"simplified.eq.{text},traditional.eq.{text}")
        .order("hsk_level", nullsfirst=False)
        .order("frequency_rank", nullsfirst=False)
        .range(start, end)
        .execute()
    )
    rows = exact.data or []
    for r in rows:
        r["match_type"] = "exact"
        r["relevance_score"] = 1

    # If no exact, try partial
    if not rows:
        partial = (
            client.table("dictionaryentry")
            .select("id,simplified,traditional,pinyin,english_definitions,hsk_level,frequency_rank,radical,old_hsk_level,new_hsk_level")
            .or_(f"simplified.ilike.%{text}%,traditional.ilike.%{text}%")
            .order("hsk_level", nullsfirst=False)
            .order("frequency_rank", nullsfirst=False)
            .range(start, end)
            .execute()
        )
        rows = partial.data or []
        for r in rows:
            r["match_type"] = "partial"
            r["relevance_score"] = 0.5

    return format_results(rows)


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


def search_pinyin(text: str, client: Client, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:

    # Preprocess the pinyin input to handle different formats
    pinyin_variants = preprocess_pinyin(text)

    start = offset
    end = offset + limit - 1

    # Try each variant in order - exact tone first
    for variant in pinyin_variants:
        exact = (
            client.table("dictionaryentry")
            .select("id,simplified,traditional,pinyin,english_definitions,hsk_level,frequency_rank,radical,old_hsk_level,new_hsk_level")
            .eq("pinyin", variant)
            .order("hsk_level", nullsfirst=False)
            .order("frequency_rank", nullsfirst=False)
            .range(start, end)
            .execute()
        )
        rows = exact.data or []
        if rows:
            for r in rows:
                r["match_type"] = "exact_tone"
                r["relevance_score"] = 1
            return format_results(rows)

    # Tone-insensitive (prefix) match
    for variant in pinyin_variants:
        tone_insensitive_text = remove_tone_numbers(variant)
        prefix = (
            client.table("dictionaryentry")
            .select("id,simplified,traditional,pinyin,english_definitions,hsk_level,frequency_rank,radical,old_hsk_level,new_hsk_level")
            .ilike("pinyin", f"{tone_insensitive_text}%")
            .order("hsk_level", nullsfirst=False)
            .order("frequency_rank", nullsfirst=False)
            .range(start, end)
            .execute()
        )
        rows = prefix.data or []
        if rows:
            for r in rows:
                r["match_type"] = "tone_insensitive"
                r["relevance_score"] = 0.8
            return format_results(rows)

    # Partial match anywhere
    partial = (
        client.table("dictionaryentry")
        .select("id,simplified,traditional,pinyin,english_definitions,hsk_level,frequency_rank,radical,old_hsk_level,new_hsk_level")
        .ilike("pinyin", f"%{text}%")
        .order("hsk_level", nullsfirst=False)
        .order("frequency_rank", nullsfirst=False)
        .range(start, end)
        .execute()
    )
    rows = partial.data or []
    for r in rows:
        r["match_type"] = "partial"
        r["relevance_score"] = 0.5

    return format_results(rows)


def search_english(text: str, client: Client, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Search for English text using LIKE-based ranking (portable across Supabase/Postgres without FTS schema).
    Priority:
    1) Direct translation style startswith matches for single words
    2) Exact-ish contains with spaces around word
    3) Partial contains
    Results are de-duplicated and paginated after combining.
    """
    words = text.split()
    is_single_word = len(words) == 1

    all_rows: List[Dict[str, Any]] = []

    base_select = "id,simplified,traditional,pinyin,english_definitions,hsk_level,frequency_rank,radical,old_hsk_level,new_hsk_level"

    if is_single_word:
        # Direct translation style: startswith the term (broader but safe for PostgREST or_ constraints)
        direct_resp = (
            client.table("dictionaryentry")
            .select(base_select)
            .ilike("english_definitions", f"{text}%")
            .order("hsk_level", nullsfirst=False)
            .order("frequency_rank", nullsfirst=False)
            .execute()
        )
        for r in direct_resp.data or []:
            r["match_type"] = "direct_translation"
            r["relevance_score"] = 2.0
        all_rows.extend(direct_resp.data or [])

    # Exact-ish contains (word boundary approximation using spaces)
    exactish_resp = (
        client.table("dictionaryentry")
        .select(base_select)
        .ilike("english_definitions", f"% {text} %")
        .order("hsk_level", nullsfirst=False)
        .order("frequency_rank", nullsfirst=False)
        .execute()
    )
    for r in exactish_resp.data or []:
        r["match_type"] = "fts_exact"
        r["relevance_score"] = 1.0
    all_rows.extend(exactish_resp.data or [])

    # Partial contains
    partial_resp = (
        client.table("dictionaryentry")
        .select(base_select)
        .ilike("english_definitions", f"%{text}%")
        .order("hsk_level", nullsfirst=False)
        .order("frequency_rank", nullsfirst=False)
        .execute()
    )
    for r in partial_resp.data or []:
        r["match_type"] = "partial"
        r["relevance_score"] = 0.5
    all_rows.extend(partial_resp.data or [])

    # De-duplicate by id preserving order
    seen = set()
    unique_rows: List[Dict[str, Any]] = []
    for r in all_rows:
        rid = r.get("id")
        if rid not in seen:
            seen.add(rid)
            unique_rows.append(r)

    # Pagination after combining
    paginated = unique_rows[offset: offset + limit]
    return format_results(paginated)