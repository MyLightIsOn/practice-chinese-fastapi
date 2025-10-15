import os
from typing import List, Dict, Any
from supabase import create_client, Client

_supabase_client: Client | None = None


def _init_client() -> Client:
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url = (
        os.getenv("SUPABASE_DB_URL")
    )
    key = (
        os.getenv("SUPABASE_ANON_KEY")

    )

    if not url or not key:
        raise RuntimeError(
            "Supabase credentials are missing. Please set SUPABASE_URL and SUPABASE_ANON_KEY (or service role)."
        )

    _supabase_client = create_client(url, key)
    return _supabase_client


def get_connection() -> Client:
    """Get the Supabase client (kept name for backward-compatibility)."""
    return _init_client()


def _fetch_related_data(client: Client, entry_ids: List[int]) -> Dict[str, Dict[int, Any]]:
    """Batch-fetch related tables and group by entry_id for formatting."""
    if not entry_ids:
        return {"pos": {}, "cls": {}, "trans": {}, "mean": {}}

    # Fetch parts of speech
    pos_resp = client.table("part_of_speech").select("entry_id,pos").in_("entry_id", entry_ids).execute()
    pos_by_entry: Dict[int, List[str]] = {}
    for row in pos_resp.data or []:
        pos_by_entry.setdefault(row["entry_id"], []).append(row["pos"])

    # Fetch classifiers
    cls_resp = client.table("classifier").select("entry_id,classifier").in_("entry_id", entry_ids).execute()
    cls_by_entry: Dict[int, List[str]] = {}
    for row in cls_resp.data or []:
        cls_by_entry.setdefault(row["entry_id"], []).append(row["classifier"])

    # Fetch transcriptions
    trans_resp = client.table("transcription").select("entry_id,system,value").in_("entry_id", entry_ids).execute()
    trans_by_entry: Dict[int, Dict[str, str]] = {}
    for row in trans_resp.data or []:
        d = trans_by_entry.setdefault(row["entry_id"], {})
        d[row["system"]] = row["value"]

    # Fetch meanings
    mean_resp = client.table("meaning").select("entry_id,definition").in_("entry_id", entry_ids).execute()
    mean_by_entry: Dict[int, List[str]] = {}
    for row in mean_resp.data or []:
        mean_by_entry.setdefault(row["entry_id"], []).append(row["definition"])

    return {
        "pos": pos_by_entry,
        "cls": cls_by_entry,
        "trans": trans_by_entry,
        "mean": mean_by_entry,
    }


def format_results(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format Supabase dictionaryentry rows with related data into API shape."""
    client = _init_client()

    # rows are dicts from Supabase select; gather ids
    entry_ids = [row["id"] for row in rows] if rows else []
    related = _fetch_related_data(client, entry_ids)

    formatted_results: List[Dict[str, Any]] = []
    for row in rows:
        entry_id = row["id"]
        hsk_data = {
            "combined": row.get("hsk_level"),
            "old": row.get("old_hsk_level"),
            "new": row.get("new_hsk_level"),
        }
        formatted_result = {
            "id": entry_id,
            "simplified": row.get("simplified"),
            "traditional": row.get("traditional"),
            "pinyin": row.get("pinyin"),
            "definition": row.get("english_definitions"),
            "hsk_level": hsk_data,
            "frequency_rank": row.get("frequency_rank"),
            "radical": row.get("radical"),
            "match_type": row.get("match_type"),
            "relevance_score": row.get("relevance_score"),
            "parts_of_speech": related["pos"].get(entry_id, []),
            "classifiers": related["cls"].get(entry_id, []),
            "transcriptions": related["trans"].get(entry_id, {}),
            "meanings": related["mean"].get(entry_id, []) or [row.get("english_definitions")],
        }
        formatted_results.append(formatted_result)

    return formatted_results