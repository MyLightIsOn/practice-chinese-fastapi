# Chinese Dictionary API Documentation

This document provides comprehensive information about the Chinese Dictionary API, including endpoints, parameters, and response formats.

## Base URL

The API is served at:

```
http://localhost:8000
```

## Endpoints

### Lookup

```
GET /lookup
```

This endpoint allows you to search for Chinese words based on the input text. The input type is automatically detected, and the search is performed accordingly.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| text | string | Yes | - | The text to search for. Can be Chinese characters, Pinyin, or English. |
| page | integer | No | 1 | Page number for pagination. Must be >= 1. |
| page_size | integer | No | 100 | Number of results per page. Must be between 1 and 100. |

#### Input Detection

The API automatically detects the type of input:

- **Chinese characters**: Search in simplified/traditional fields
- **Pinyin**: Search in pinyin field
- **English**: Search in definitions using Full-Text Search (FTS)

#### Search Behavior

The search behavior varies depending on the detected input type:

##### Chinese Search

1. **Exact Match**: First tries to find entries where the simplified or traditional characters exactly match the input
2. **Partial Match**: If no exact matches are found, looks for entries containing the input characters

##### Pinyin Search

1. **Exact Tone Match**: First tries to find entries with exact pinyin match (including tones)
2. **Tone-Insensitive Match**: If no exact matches, tries matching without considering tones
3. **Partial Match**: If still no matches, looks for entries containing the input pinyin

The API handles various pinyin input formats:
- With spaces: "ni3 hao3"
- Without spaces: "ni3hao3"
- Without tones: "nihao"

##### English Search

1. **Exact Match**: First tries to find entries with the exact English definition
2. **FTS Match**: If no exact matches, uses Full-Text Search with ranking
3. **Partial Match**: If still no matches, looks for entries containing the input text

For single-word queries, wildcards are added (e.g., "word*") to improve matching.

## Response Format

### Success Response

```json
{
  "input_type": "chinese|pinyin|english",
  "results": [
    {
      "id": 123,
      "simplified": "你好",
      "traditional": "你好",
      "pinyin": "ni3 hao3",
      "definition": "hello",
      "hsk_level": {
        "combined": 1,
        "old": 1,
        "new": 1
      },
      "frequency_rank": 42,
      "radical": "亻",
      "match_type": "exact|partial|exact_tone|tone_insensitive|fts_exact|fts",
      "relevance_score": 1.0,
      "parts_of_speech": ["greeting", "interjection"],
      "classifiers": ["ge4"],
      "transcriptions": {
        "zhuyin": "ㄋㄧˇ ㄏㄠˇ",
        "wadegiles": "ni³ hao³"
      },
      "meanings": ["hello", "hi", "how are you"]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_count": 42,
    "total_pages": 1
  }
}
```

### Error Response

```json
{
  "detail": "Error message"
}
```

## Response Fields

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| input_type | string | The detected type of input: "chinese", "pinyin", or "english" |
| results | array | Array of dictionary entries matching the search criteria |
| pagination | object | Pagination information |

### Dictionary Entry Fields

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier for the dictionary entry |
| simplified | string | Simplified Chinese characters |
| traditional | string | Traditional Chinese characters |
| pinyin | string | Pinyin pronunciation with tone numbers |
| definition | string | English definition (kept for backward compatibility) |
| hsk_level | object | HSK proficiency level information |
| frequency_rank | integer | Word frequency ranking (lower is more common) |
| radical | string | Character radical |
| match_type | string | Type of match (exact, partial, etc.) |
| relevance_score | number | Score indicating match quality (0-1) |
| parts_of_speech | array | Array of parts of speech |
| classifiers | array | Array of measure words/classifiers |
| transcriptions | object | Alternative transcription systems |
| meanings | array | Array of detailed meanings |

### HSK Level Fields

| Field | Type | Description |
|-------|------|-------------|
| combined | integer | Combined HSK level (1-6) |
| old | integer | Old HSK level (1-6) |
| new | integer | New HSK level (1-9) |

### Pagination Fields

| Field | Type | Description |
|-------|------|-------------|
| page | integer | Current page number |
| page_size | integer | Number of results per page |
| total_count | integer | Total number of matching entries |
| total_pages | integer | Total number of pages |

## Match Types and Relevance Scores

The API uses different match types and relevance scores to indicate the quality of the match:

| Match Type | Relevance Score | Description |
|------------|----------------|-------------|
| exact | 1.0 | Exact match in simplified/traditional Chinese |
| partial | 0.5 | Partial match in simplified/traditional Chinese |
| exact_tone | 1.0 | Exact match in pinyin with tones |
| tone_insensitive | 0.8 | Match in pinyin ignoring tones |
| fts_exact | 1.0 | Exact match in English definition |
| fts | 0.9 | Full-Text Search match in English definition |
| partial | 0.5 | Partial match in English definition |

## Examples

### Chinese Search

Request:
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
      "definition": "hello",
      "hsk_level": {
        "combined": 1,
        "old": 1,
        "new": 1
      },
      "frequency_rank": 42,
      "radical": "亻",
      "match_type": "exact",
      "relevance_score": 1.0,
      "parts_of_speech": ["greeting", "interjection"],
      "classifiers": ["ge4"],
      "transcriptions": {
        "zhuyin": "ㄋㄧˇ ㄏㄠˇ",
        "wadegiles": "ni³ hao³"
      },
      "meanings": ["hello", "hi", "how are you"]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_count": 1,
    "total_pages": 1
  }
}
```

### Pinyin Search

Request:
```
GET /lookup?text=ni3hao3
```

Response:
```json
{
  "input_type": "pinyin",
  "results": [
    {
      "id": 123,
      "simplified": "你好",
      "traditional": "你好",
      "pinyin": "ni3 hao3",
      "definition": "hello",
      "hsk_level": {
        "combined": 1,
        "old": 1,
        "new": 1
      },
      "frequency_rank": 42,
      "radical": "亻",
      "match_type": "exact_tone",
      "relevance_score": 1.0,
      "parts_of_speech": ["greeting", "interjection"],
      "classifiers": ["ge4"],
      "transcriptions": {
        "zhuyin": "ㄋㄧˇ ㄏㄠˇ",
        "wadegiles": "ni³ hao³"
      },
      "meanings": ["hello", "hi", "how are you"]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_count": 1,
    "total_pages": 1
  }
}
```

### English Search

Request:
```
GET /lookup?text=hello
```

Response:
```json
{
  "input_type": "english",
  "results": [
    {
      "id": 123,
      "simplified": "你好",
      "traditional": "你好",
      "pinyin": "ni3 hao3",
      "definition": "hello",
      "hsk_level": {
        "combined": 1,
        "old": 1,
        "new": 1
      },
      "frequency_rank": 42,
      "radical": "亻",
      "match_type": "fts_exact",
      "relevance_score": 1.0,
      "parts_of_speech": ["greeting", "interjection"],
      "classifiers": ["ge4"],
      "transcriptions": {
        "zhuyin": "ㄋㄧˇ ㄏㄠˇ",
        "wadegiles": "ni³ hao³"
      },
      "meanings": ["hello", "hi", "how are you"]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_count": 1,
    "total_pages": 1
  }
}
```

### Pagination Example

Request:
```
GET /lookup?text=a&page=2&page_size=10
```

Response:
```json
{
  "input_type": "english",
  "results": [
    {
      "id": 456,
      "simplified": "爱",
      "traditional": "愛",
      "pinyin": "ai4",
      "definition": "to love, affection, to be fond of, to like",
      "hsk_level": {
        "combined": 2,
        "old": 2,
        "new": 2
      },
      "frequency_rank": 102,
      "radical": "心",
      "match_type": "fts",
      "relevance_score": 0.9,
      "parts_of_speech": ["verb", "noun"],
      "classifiers": [],
      "transcriptions": {
        "zhuyin": "ㄞˋ",
        "wadegiles": "ai⁴"
      },
      "meanings": ["to love", "to be fond of", "to like", "affection"]
    }
  ],
  "pagination": {
    "page": 2,
    "page_size": 10,
    "total_count": 42,
    "total_pages": 5
  }
}
```

## Error Handling

### Invalid Parameters

If you provide invalid parameters, the API will return an appropriate error message:

Request:
```
GET /lookup?text=
```

Response:
```json
{
  "detail": "Text parameter cannot be empty"
}
```

Request:
```
GET /lookup?text=hello&page=0
```

Response:
```json
{
  "detail": [
    {
      "loc": ["query", "page"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge",
      "ctx": {"limit_value": 1}
    }
  ]
}
```