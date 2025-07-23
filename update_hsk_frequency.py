import json
import sqlite3
import re

def extract_hsk_level(level_array):
    """
    Extract the HSK level from the level array.
    Prioritize the new HSK system, fall back to old if needed.
    For 'new-7+', return 7.
    """
    if not level_array:
        return None
    
    # Look for new HSK level first
    for level in level_array:
        if level.startswith("new-"):
            # Handle "new-7+" case
            if level == "new-7+":
                return 7
            # Extract the number from "new-X"
            match = re.search(r'new-(\d+)', level)
            if match:
                return int(match.group(1))
    
    # Fall back to old HSK level if no new level found
    for level in level_array:
        if level.startswith("old-"):
            match = re.search(r'old-(\d+)', level)
            if match:
                return int(match.group(1))
    
    return None

def update_database():
    """
    Update the database with HSK level and frequency rank data from complete.json
    """
    print("Loading complete.json...")
    with open('complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} entries from complete.json")
    
    # Connect to the database
    print("Connecting to database...")
    conn = sqlite3.connect('cedict.db')
    cursor = conn.cursor()
    
    # Get all existing entries from the database
    cursor.execute("SELECT id, simplified, traditional FROM dictionaryentry")
    db_entries = cursor.fetchall()
    
    # Create a dictionary for faster lookup
    db_dict = {}
    for id, simplified, traditional in db_entries:
        db_dict[(simplified, traditional)] = id
    
    print(f"Found {len(db_entries)} entries in the database")
    
    # Prepare for batch updates
    updates = []
    not_found = []
    
    # Process each entry from the JSON file
    for entry in data:
        simplified = entry['simplified']
        frequency = entry.get('frequency')
        hsk_level = extract_hsk_level(entry.get('level', []))
        
        # Get all traditional forms
        for form in entry.get('forms', []):
            traditional = form.get('traditional', simplified)
            
            # Try to find this entry in the database
            if (simplified, traditional) in db_dict:
                entry_id = db_dict[(simplified, traditional)]
                updates.append((hsk_level, frequency, entry_id))
            else:
                not_found.append((simplified, traditional))
    
    print(f"Found matches for {len(updates)} entries")
    print(f"Could not find matches for {len(not_found)} entries")
    
    # Update the database in batches
    batch_size = 1000
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i+batch_size]
        cursor.executemany(
            "UPDATE dictionaryentry SET hsk_level = ?, frequency_rank = ? WHERE id = ?",
            batch
        )
        conn.commit()
        print(f"Updated batch {i//batch_size + 1}/{(len(updates)-1)//batch_size + 1}")
    
    # Verify the updates
    cursor.execute("SELECT COUNT(*) FROM dictionaryentry WHERE hsk_level IS NOT NULL")
    hsk_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM dictionaryentry WHERE frequency_rank IS NOT NULL")
    freq_count = cursor.fetchone()[0]
    
    print(f"Entries with HSK level: {hsk_count}")
    print(f"Entries with frequency rank: {freq_count}")
    
    conn.close()
    print("Database update completed")

if __name__ == "__main__":
    update_database()