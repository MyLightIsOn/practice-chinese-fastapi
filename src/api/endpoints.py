from fastapi import APIRouter, Query, HTTPException
from enum import Enum
from src.db.connection import get_connection
from src.detection.input_detection import detect_input_type
from src.search.search import search_chinese, search_pinyin, search_english
from src.api.exercise_routes import router as exercise_router

router = APIRouter()

router.include_router(exercise_router, prefix="/exercises")

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
    - English: Search in definitions using FTS

    Results are ranked based on the input type and include a match_type and relevance_score.
    """
    if not text:
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty")

    conn = get_connection()
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
            SELECT COUNT(*)
            FROM dictionaryentry d
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