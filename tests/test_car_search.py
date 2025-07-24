import sqlite3
import json
import sys
import os

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.search.search import search_english

# Connect to the database
conn = sqlite3.connect('cedict.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Search for "car"
results = search_english("car", cursor)

# Print the results
print(json.dumps({
    "input_type": "english",
    "results": results,
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_count": len(results),
        "total_pages": 1
    }
}, indent=4))

# Check if "汽车" is in the results
found = False
for result in results:
    if result.get("simplified") == "汽车":
        print(f"\nFound 汽车 at position {results.index(result) + 1}")
        found = True
        break

if not found:
    print("\n汽车 not found in the top results")

# Close the connection
conn.close()