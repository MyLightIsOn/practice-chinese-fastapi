from fastapi import FastAPI, Query
import sqlite3
from enum import Enum

app = FastAPI()
conn = sqlite3.connect("cedict.db", check_same_thread=False)

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
    match_type: MatchType = MatchType.CONTAINS,
    search_field: str = Query("all", description="Field to search: simplified, traditional, pinyin, definition, or all")
):
    cursor = conn.cursor()
    
    if search_field == "definition":
        # Use FTS for English definitions
        if match_type == MatchType.EXACT:
            query = """
                SELECT d.* FROM dictionaryentry d
                JOIN fts_english_definitions fts ON d.id = fts.id
                WHERE fts.content = ?
            """
        else:  # CONTAINS
            query = """
                SELECT d.* FROM dictionaryentry d
                JOIN fts_english_definitions fts ON d.id = fts.id
                WHERE fts.content MATCH ?
            """
        cursor.execute(query, (text,))
    elif search_field in ["simplified", "traditional", "pinyin"]:
        # Use exact match or LIKE based on match_type
        if match_type == MatchType.EXACT:
            query = f"SELECT * FROM dictionaryentry WHERE {search_field} = ?"
            cursor.execute(query, (text,))
        else:  # CONTAINS
            query = f"SELECT * FROM dictionaryentry WHERE {search_field} LIKE ?"
            cursor.execute(query, (f"%{text}%",))
    else:  # "all" or any other value
        # Search across all fields
        if match_type == MatchType.EXACT:
            query = """
                SELECT * FROM dictionaryentry 
                WHERE simplified = ? OR traditional = ? OR pinyin = ?
                UNION
                SELECT d.* FROM dictionaryentry d
                JOIN fts_english_definitions fts ON d.id = fts.id
                WHERE fts.content = ?
            """
            cursor.execute(query, (text, text, text, text))
        else:  # CONTAINS
            query = """
                SELECT * FROM dictionaryentry 
                WHERE simplified LIKE ? OR traditional LIKE ? OR pinyin LIKE ?
                UNION
                SELECT d.* FROM dictionaryentry d
                JOIN fts_english_definitions fts ON d.id = fts.id
                WHERE fts.content MATCH ?
            """
            cursor.execute(query, (f"%{text}%", f"%{text}%", f"%{text}%", text))
    
    results = cursor.fetchall()
    return [{"simplified": row[1], "traditional": row[2], "pinyin": row[3], "definition": row[4]} for row in results]