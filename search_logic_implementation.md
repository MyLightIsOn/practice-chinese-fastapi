# Search Logic Implementation

This document describes the implementation of the new search logic for the Chinese dictionary lookup system.

## Overview

The new search logic automatically detects the type of input (Chinese, Pinyin, or English) and applies the appropriate search strategy based on the detected input type. This eliminates the need for users to explicitly select the type of search they want to perform.

## Input Type Detection

The system automatically detects the input type using the following logic:

### Chinese Characters
- Detected using Unicode code point ranges for CJK Unified Ideographs
- Function: `contains_chinese(text)`

### Pinyin
- Detected using pattern matching for Pinyin syllables with or without tone numbers
- Handles various formats: with spaces ("ni3 hao3"), without spaces ("ni3hao3"), without tones ("nihao")
- Excludes common English words to avoid false positives
- Function: `is_pinyin(text)`

### English
- Detected when the input is neither Chinese nor Pinyin
- Includes special handling for common English words and phrases
- Function: `is_english(text)`

## Search Priority Logic

The system applies different search strategies based on the detected input type:

### Chinese Search Priority
1. First try exact matches in simplified/traditional characters
2. If no exact matches found, try partial matches
3. Results are ranked by HSK level (easier words first) and frequency (more common words first)
4. Function: `search_chinese(text, cursor, limit, offset)`

### Pinyin Search Priority
1. Try exact pinyin match with tones
2. If no exact matches, try tone-insensitive match
3. If still no matches, try partial pinyin match
4. Results are ranked by HSK level and frequency
5. Includes preprocessing to handle different Pinyin formats
6. Function: `search_pinyin(text, cursor, limit, offset)`

### English Search Priority
1. Try exact matches in definitions
2. If no exact matches, use Full-Text Search (FTS) with relevance ranking
3. If still no results, try a more relaxed partial match
4. Results are ranked by match quality, HSK level, and frequency
5. Function: `search_english(text, cursor, limit, offset)`

## Result Ranking

Results are ranked based on the input type and include a match_type and relevance_score:

### Chinese/Pinyin Ranking
1. Exact matches first (relevance_score = 1.0)
2. Tone-insensitive matches (relevance_score = 0.8)
3. Partial matches (relevance_score = 0.5)
4. Within each match type, results are sorted by:
   - HSK level (ascending, easier words first)
   - Frequency rank (ascending, more common words first)

### English Ranking
1. Exact matches in definitions (relevance_score = 1.0)
2. FTS matches with quality score (relevance_score = 0.9)
3. Partial matches (relevance_score = 0.5)
4. Within each match type, results are sorted by:
   - FTS match quality (for FTS matches)
   - HSK level (ascending)
   - Frequency rank (ascending)

## Pagination

The system supports pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Number of results per page (default: 20, max: 100)

The response includes pagination metadata:
- `page`: Current page number
- `page_size`: Number of results per page
- `total_count`: Total number of matching results
- `total_pages`: Total number of pages

## Response Format

The response includes:
- `input_type`: Detected input type (chinese, pinyin, or english)
- `results`: Array of matching dictionary entries
- `pagination`: Pagination metadata

Each result includes:
- `id`: Dictionary entry ID
- `simplified`: Simplified Chinese characters
- `traditional`: Traditional Chinese characters
- `pinyin`: Pinyin representation
- `definition`: English definition
- `hsk_level`: HSK level (difficulty)
- `frequency_rank`: Frequency ranking
- `match_type`: Type of match (exact, partial, etc.)
- `relevance_score`: Relevance score for ranking

## Example Usage

```
GET /lookup?text=你好
```

Response:
```json
{
  "input_type": "chinese",
  "results": [
    {
      "id": 123,
      "simplified": "你好",
      "traditional": "你好",
      "pinyin": "ni3 hao3",
      "definition": "hello; hi",
      "hsk_level": 1,
      "frequency_rank": 100,
      "match_type": "exact",
      "relevance_score": 1.0
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 1,
    "total_pages": 1
  }
}
```

## Implementation Details

The implementation includes the following key components:

1. **Input Type Detection Functions**:
   - `contains_chinese(text)`: Detects Chinese characters
   - `is_pinyin(text)`: Detects Pinyin input
   - `is_english(text)`: Detects English input
   - `detect_input_type(text)`: Determines the input type

2. **Search Functions**:
   - `search_chinese(text, cursor, limit, offset)`: Searches for Chinese characters
   - `search_pinyin(text, cursor, limit, offset)`: Searches for Pinyin
   - `search_english(text, cursor, limit, offset)`: Searches for English text

3. **Helper Functions**:
   - `preprocess_pinyin(text)`: Preprocesses Pinyin input to handle different formats
   - `remove_tone_numbers(pinyin)`: Removes tone numbers from Pinyin
   - `format_results(results)`: Formats the database results into a consistent structure

4. **Lookup Endpoint**:
   - `lookup(text, page, page_size)`: Main endpoint that detects input type and performs the appropriate search

This implementation provides a seamless search experience for users, automatically detecting the input type and applying the appropriate search strategy without requiring explicit user selection.