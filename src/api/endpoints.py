from fastapi import APIRouter, Query, HTTPException
from enum import Enum
from src.db.connection import get_connection
from src.detection.input_detection import detect_input_type
from src.search.search import search_chinese, search_pinyin, search_english

router = APIRouter()

class MatchType(str, Enum):
    EXACT = "exact"
    CONTAINS = "contains"


@router.get("/lookup")
def lookup(
        text: str = Query(..., min_length=1),
        page: int = Query(1, ge=1, description="Page number for pagination"),
        page_size: int = Query(100, ge=1, le=100, description="Number of results per page")
):
    """
    Lookup Chinese words based on the input text.

    The input type is automatically detected:
    - Chinese characters: Search in simplified/traditional
    - Pinyin: Search in pinyin field
    - English: Search in definitions

    Results are ranked based on the input type and include a match_type and relevance_score.
    """
    if not text:
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty")

    client = get_connection()

    # Calculate offset for pagination
    offset = (page - 1) * page_size

    # Detect input type
    input_type = detect_input_type(text)

    # Search based on input type
    try:
        if input_type == "chinese":
            results = search_chinese(text, client, limit=page_size, offset=offset)
            count_resp = client.table("dictionaryentry").select("id", count="exact").or_(f"simplified.ilike.%{text}%,traditional.ilike.%{text}%").execute()
        elif input_type == "pinyin":
            results = search_pinyin(text, client, limit=page_size, offset=offset)
            count_resp = client.table("dictionaryentry").select("id", count="exact").ilike("pinyin", f"%{text}%").execute()
        else:  # english
            results = search_english(text, client, limit=page_size, offset=offset)
            count_resp = client.table("dictionaryentry").select("id", count="exact").ilike("english_definitions", f"%{text}%").execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    total_count = (count_resp.count or 0) if hasattr(count_resp, "count") else 0
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