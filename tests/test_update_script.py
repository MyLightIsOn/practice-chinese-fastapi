import json
import sqlite3
import sys
from archive.update_hsk_frequency import extract_hsk_levels, extract_radical, extract_pos, extract_classifiers, extract_transcriptions, extract_meanings

def test_update_with_sample():
    """
    Test the update functions with a small sample of data from complete.json
    """
    print("Loading complete.json...")
    with open('../complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Take only the first 10 entries for testing
    sample_data = data[:10]
    print(f"Using {len(sample_data)} sample entries from complete.json")
    
    # Connect to the database
    print("Connecting to database...")
    conn = sqlite3.connect('../archive/cedict.db')
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
    
    # Process each entry from the sample data
    for entry in sample_data:
        simplified = entry['simplified']
        frequency = entry.get('frequency')
        old_hsk_level, new_hsk_level = extract_hsk_levels(entry.get('level', []))
        radical = extract_radical(entry)
        pos_list = extract_pos(entry)
        
        print(f"\nProcessing entry: {simplified}")
        print(f"  Radical: {radical}")
        print(f"  Old HSK: {old_hsk_level}, New HSK: {new_hsk_level}")
        print(f"  Parts of speech: {pos_list}")
        
        # Get all traditional forms
        for form in entry.get('forms', []):
            traditional = form.get('traditional', simplified)
            print(f"  Traditional form: {traditional}")
            
            # Try to find this entry in the database
            if (simplified, traditional) in db_dict:
                entry_id = db_dict[(simplified, traditional)]
                print(f"  Found in database with ID: {entry_id}")
                
                # Update main entry
                main_updates.append((radical, old_hsk_level, new_hsk_level, old_hsk_level or new_hsk_level, frequency, entry_id))
                
                # Add parts of speech
                for pos in pos_list:
                    pos_inserts.append((entry_id, pos))
                    print(f"  Adding part of speech: {pos}")
                
                # Add classifiers
                classifiers = extract_classifiers(form)
                for classifier in classifiers:
                    classifier_inserts.append((entry_id, classifier))
                    print(f"  Adding classifier: {classifier}")
                
                # Add transcriptions
                transcriptions = extract_transcriptions(form)
                for system, value in transcriptions:
                    transcription_inserts.append((entry_id, system, value))
                    print(f"  Adding transcription: {system} = {value}")
                
                # Add meanings
                meanings = extract_meanings(form)
                for meaning in meanings:
                    meaning_inserts.append((entry_id, meaning))
                    print(f"  Adding meaning: {meaning}")
            else:
                not_found.append((simplified, traditional))
                print(f"  Not found in database")
    
    print(f"\nFound matches for {len(main_updates)} entries")
    print(f"Could not find matches for {len(not_found)} entries")
    print(f"Total parts of speech to insert: {len(pos_inserts)}")
    print(f"Total classifiers to insert: {len(classifier_inserts)}")
    print(f"Total transcriptions to insert: {len(transcription_inserts)}")
    print(f"Total meanings to insert: {len(meaning_inserts)}")
    
    # Automatically proceed with the update
    print("\nAutomatically proceeding with database update...")
    
    try:
        # Start a transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Update the main dictionaryentry table
        print("\nUpdating dictionaryentry table...")
        for update in main_updates:
            cursor.execute(
                """UPDATE dictionaryentry 
                   SET radical = ?, old_hsk_level = ?, new_hsk_level = ?, 
                       hsk_level = ?, frequency_rank = ? 
                   WHERE id = ?""",
                update
            )
            print(f"Updated entry ID: {update[5]}")
        
        # Insert parts of speech
        print("\nInserting parts of speech...")
        for entry_id, pos in pos_inserts:
            cursor.execute(
                "INSERT INTO part_of_speech (entry_id, pos) VALUES (?, ?)",
                (entry_id, pos)
            )
        
        # Insert classifiers
        print("\nInserting classifiers...")
        for entry_id, classifier in classifier_inserts:
            cursor.execute(
                "INSERT INTO classifier (entry_id, classifier) VALUES (?, ?)",
                (entry_id, classifier)
            )
        
        # Insert transcriptions
        print("\nInserting transcriptions...")
        for entry_id, system, value in transcription_inserts:
            cursor.execute(
                "INSERT INTO transcription (entry_id, system, value) VALUES (?, ?, ?)",
                (entry_id, system, value)
            )
        
        # Insert meanings
        print("\nInserting meanings...")
        for entry_id, meaning in meaning_inserts:
            cursor.execute(
                "INSERT INTO meaning (entry_id, definition) VALUES (?, ?)",
                (entry_id, meaning)
            )
        
        # Commit the transaction
        conn.commit()
        print("\nSample data update completed successfully!")
        
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
        
        print(f"\nEntries with old HSK level: {old_hsk_count}")
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

if __name__ == "__main__":
    test_update_with_sample()