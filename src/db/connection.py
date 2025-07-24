import sqlite3
from typing import List, Dict, Any, Tuple

# Create a database connection
conn = sqlite3.connect("cedict.db", check_same_thread=False)

def get_connection():
    """Get the database connection."""
    return conn

def format_results(results: List[Tuple]) -> List[Dict[str, Any]]:
    """Format the database results into a list of dictionaries with additional related data."""
    formatted_results = []
    cursor = conn.cursor()

    for row in results:
        entry_id = row[0]

        # Get parts of speech
        cursor.execute(
            "SELECT pos FROM part_of_speech WHERE entry_id = ?",
            (entry_id,)
        )
        parts_of_speech = [pos[0] for pos in cursor.fetchall()]

        # Get classifiers
        cursor.execute(
            "SELECT classifier FROM classifier WHERE entry_id = ?",
            (entry_id,)
        )
        classifiers = [cls[0] for cls in cursor.fetchall()]

        # Get transcriptions
        cursor.execute(
            "SELECT system, value FROM transcription WHERE entry_id = ?",
            (entry_id,)
        )
        transcriptions_rows = cursor.fetchall()
        transcriptions = {}
        for system, value in transcriptions_rows:
            transcriptions[system] = value

        # Get meanings
        cursor.execute(
            "SELECT definition FROM meaning WHERE entry_id = ?",
            (entry_id,)
        )
        meanings = [meaning[0] for meaning in cursor.fetchall()]

        # Format HSK levels
        hsk_data = {
            "combined": row[5],  # Keep the original hsk_level for backward compatibility
            "old": row[8],  # old_hsk_level
            "new": row[9]  # new_hsk_level
        }

        # Create the formatted result
        formatted_result = {
            "id": entry_id,
            "simplified": row[1],
            "traditional": row[2],
            "pinyin": row[3],
            "definition": row[4],  # Keep the original definition for backward compatibility
            "hsk_level": hsk_data,
            "frequency_rank": row[6],
            "radical": row[7],
            "match_type": row[10],
            "relevance_score": row[11],
            "parts_of_speech": parts_of_speech,
            "classifiers": classifiers,
            "transcriptions": transcriptions,
            "meanings": meanings if meanings else [row[4]]  # Use original definition if no separate meanings
        }

        formatted_results.append(formatted_result)

    return formatted_results