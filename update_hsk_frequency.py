import json
import sqlite3
import re
import sys

def extract_hsk_levels(level_array):
    """
    Extract both old and new HSK levels from the level array.
    For 'new-7+', return 7 for new HSK level.
    Returns a tuple of (old_hsk_level, new_hsk_level).
    """
    if not level_array:
        return None, None
    
    old_hsk_level = None
    new_hsk_level = None
    
    # Extract new HSK level
    for level in level_array:
        if level.startswith("new-"):
            # Handle "new-7+" case
            if level == "new-7+":
                new_hsk_level = 7
                break
            # Extract the number from "new-X"
            match = re.search(r'new-(\d+)', level)
            if match:
                new_hsk_level = int(match.group(1))
                break
    
    # Extract old HSK level
    for level in level_array:
        if level.startswith("old-"):
            match = re.search(r'old-(\d+)', level)
            if match:
                old_hsk_level = int(match.group(1))
                break
    
    return old_hsk_level, new_hsk_level

def extract_radical(entry):
    """
    Extract the radical from the entry.
    """
    return entry.get('radical')

def extract_pos(entry):
    """
    Extract parts of speech from the entry.
    """
    return entry.get('pos', [])

def extract_classifiers(form):
    """
    Extract classifiers from the form.
    """
    return form.get('classifiers', [])

def extract_transcriptions(form):
    """
    Extract transcriptions from the form.
    Returns a list of (system, value) tuples.
    """
    transcriptions = []
    for system, value in form.get('transcriptions', {}).items():
        transcriptions.append((system, value))
    return transcriptions

def extract_meanings(form):
    """
    Extract meanings from the form.
    """
    return form.get('meanings', [])

def update_database():
    """
    Update the database with data from complete.json including:
    - HSK levels (old and new)
    - Frequency rank
    - Radical
    - Parts of speech
    - Classifiers
    - Transcriptions
    - Meanings
    """
    print("Loading complete.json...")
    with open('complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} entries from complete.json")
    
    # Connect to the database
    print("Connecting to database...")
    conn = sqlite3.connect('cedict.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Get all existing entries from the database
    cursor.execute("SELECT id, simplified, traditional FROM dictionaryentry")
    db_entries = cursor.fetchall()
    
    # Create a dictionary for faster lookup
    db_dict = {}
    for id, simplified, traditional in db_entries:
        db_dict[(simplified, traditional)] = id
    
    print(f"Found {len(db_entries)} entries in the database")
    
    # Prepare for batch updates
    main_updates = []  # For dictionaryentry table
    pos_inserts = []   # For part_of_speech table
    classifier_inserts = []  # For classifier table
    transcription_inserts = []  # For transcription table
    meaning_inserts = []  # For meaning table
    not_found = []
    
    # Process each entry from the JSON file
    for entry in data:
        simplified = entry['simplified']
        frequency = entry.get('frequency')
        old_hsk_level, new_hsk_level = extract_hsk_levels(entry.get('level', []))
        radical = extract_radical(entry)
        pos_list = extract_pos(entry)
        
        # Get all traditional forms
        for form in entry.get('forms', []):
            traditional = form.get('traditional', simplified)
            
            # Try to find this entry in the database
            if (simplified, traditional) in db_dict:
                entry_id = db_dict[(simplified, traditional)]
                
                # Update main entry
                main_updates.append((radical, old_hsk_level, new_hsk_level, old_hsk_level or new_hsk_level, frequency, entry_id))
                
                # Add parts of speech
                for pos in pos_list:
                    pos_inserts.append((entry_id, pos))
                
                # Add classifiers
                for classifier in extract_classifiers(form):
                    classifier_inserts.append((entry_id, classifier))
                
                # Add transcriptions
                for system, value in extract_transcriptions(form):
                    transcription_inserts.append((entry_id, system, value))
                
                # Add meanings
                for meaning in extract_meanings(form):
                    meaning_inserts.append((entry_id, meaning))
            else:
                not_found.append((simplified, traditional))
    
    print(f"Found matches for {len(main_updates)} entries")
    print(f"Could not find matches for {len(not_found)} entries")
    
    try:
        # Start a transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Clear existing data from related tables
        print("Clearing existing data from related tables...")
        cursor.execute("DELETE FROM part_of_speech")
        cursor.execute("DELETE FROM classifier")
        cursor.execute("DELETE FROM transcription")
        cursor.execute("DELETE FROM meaning")
        
        # Update the main dictionaryentry table in batches
        print("Updating dictionaryentry table...")
        batch_size = 1000
        for i in range(0, len(main_updates), batch_size):
            batch = main_updates[i:i+batch_size]
            cursor.executemany(
                """UPDATE dictionaryentry 
                   SET radical = ?, old_hsk_level = ?, new_hsk_level = ?, 
                       hsk_level = ?, frequency_rank = ? 
                   WHERE id = ?""",
                batch
            )
            print(f"Updated dictionaryentry batch {i//batch_size + 1}/{(len(main_updates)-1)//batch_size + 1}")
        
        # Insert parts of speech in batches
        print(f"Inserting {len(pos_inserts)} parts of speech...")
        for i in range(0, len(pos_inserts), batch_size):
            batch = pos_inserts[i:i+batch_size]
            cursor.executemany(
                "INSERT INTO part_of_speech (entry_id, pos) VALUES (?, ?)",
                batch
            )
            print(f"Inserted part_of_speech batch {i//batch_size + 1}/{(len(pos_inserts)-1)//batch_size + 1 if len(pos_inserts) > 0 else 1}")
        
        # Insert classifiers in batches
        print(f"Inserting {len(classifier_inserts)} classifiers...")
        for i in range(0, len(classifier_inserts), batch_size):
            batch = classifier_inserts[i:i+batch_size]
            cursor.executemany(
                "INSERT INTO classifier (entry_id, classifier) VALUES (?, ?)",
                batch
            )
            print(f"Inserted classifier batch {i//batch_size + 1}/{(len(classifier_inserts)-1)//batch_size + 1 if len(classifier_inserts) > 0 else 1}")
        
        # Insert transcriptions in batches
        print(f"Inserting {len(transcription_inserts)} transcriptions...")
        for i in range(0, len(transcription_inserts), batch_size):
            batch = transcription_inserts[i:i+batch_size]
            cursor.executemany(
                "INSERT INTO transcription (entry_id, system, value) VALUES (?, ?, ?)",
                batch
            )
            print(f"Inserted transcription batch {i//batch_size + 1}/{(len(transcription_inserts)-1)//batch_size + 1 if len(transcription_inserts) > 0 else 1}")
        
        # Insert meanings in batches
        print(f"Inserting {len(meaning_inserts)} meanings...")
        for i in range(0, len(meaning_inserts), batch_size):
            batch = meaning_inserts[i:i+batch_size]
            cursor.executemany(
                "INSERT INTO meaning (entry_id, definition) VALUES (?, ?)",
                batch
            )
            print(f"Inserted meaning batch {i//batch_size + 1}/{(len(meaning_inserts)-1)//batch_size + 1 if len(meaning_inserts) > 0 else 1}")
        
        # Commit the transaction
        conn.commit()
        
        # Verify the updates
        cursor.execute("SELECT COUNT(*) FROM dictionaryentry WHERE old_hsk_level IS NOT NULL")
        old_hsk_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dictionaryentry WHERE new_hsk_level IS NOT NULL")
        new_hsk_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dictionaryentry WHERE radical IS NOT NULL")
        radical_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM part_of_speech")
        pos_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM classifier")
        classifier_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transcription")
        transcription_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM meaning")
        meaning_count = cursor.fetchone()[0]
        
        print(f"Entries with old HSK level: {old_hsk_count}")
        print(f"Entries with new HSK level: {new_hsk_count}")
        print(f"Entries with radical: {radical_count}")
        print(f"Total parts of speech: {pos_count}")
        print(f"Total classifiers: {classifier_count}")
        print(f"Total transcriptions: {transcription_count}")
        print(f"Total meanings: {meaning_count}")
        
    except sqlite3.Error as e:
        # Roll back any changes if an error occurs
        conn.rollback()
        print(f"Database error: {e}", file=sys.stderr)
    except Exception as e:
        # Roll back any changes if an error occurs
        conn.rollback()
        print(f"Error: {e}", file=sys.stderr)
    finally:
        # Close the connection
        conn.close()
        
    print("Database update completed")

if __name__ == "__main__":
    update_database()