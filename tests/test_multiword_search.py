import sqlite3
import json
from src.search.search import search_english

# Connect to the database
conn = sqlite3.connect('../archive/cedict.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Test a multi-word query
query = "train station"
print(f"Testing multi-word query: '{query}'")
results = search_english(query, cursor)

# Print the first few results
print(json.dumps({
    "input_type": "english",
    "results": results[:5],  # Just show the first 5 results for brevity
    "pagination": {
        "page": 1,
        "page_size": 100,
        "total_count": len(results),
        "total_pages": 1
    }
}, indent=4))

# Test another single-word query
query = "book"
print(f"\nTesting single-word query: '{query}'")
results = search_english(query, cursor)

# Check if there are direct translations
direct_translations = [r for r in results if r.get("match_type") == "direct_translation"]
print(f"Found {len(direct_translations)} direct translations for '{query}'")

# Print the first few direct translations
if direct_translations:
    print(json.dumps(direct_translations[:3], indent=4))  # Just show the first 3 for brevity

# Close the connection
conn.close()