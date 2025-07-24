import sqlite3
import sys

def migrate_database():
    """
    Perform database schema migration for Chinese dictionary enhancement:
    1. Add radical column to dictionaryentry table
    2. Split hsk_level into old_hsk_level and new_hsk_level
    3. Create new related tables (part_of_speech, classifier, transcription, meaning)
    4. Add appropriate foreign key constraints and indexes
    """
    print("Starting database schema migration...")
    
    # Connect to the database
    try:
        conn = sqlite3.connect('cedict.db')
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Start a transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. Modify the dictionaryentry table
        print("Modifying dictionaryentry table...")
        
        # Add radical column
        cursor.execute("ALTER TABLE dictionaryentry ADD COLUMN radical VARCHAR")
        
        # Add old_hsk_level and new_hsk_level columns
        cursor.execute("ALTER TABLE dictionaryentry ADD COLUMN old_hsk_level INTEGER")
        cursor.execute("ALTER TABLE dictionaryentry ADD COLUMN new_hsk_level INTEGER")
        
        # Migrate existing hsk_level data to appropriate columns
        # This is a placeholder - actual data migration will be handled in the data import script
        print("Note: Existing HSK level data will be migrated in the data import script")
        
        # 2. Create part_of_speech table
        print("Creating part_of_speech table...")
        cursor.execute("""
        CREATE TABLE part_of_speech (
            id INTEGER PRIMARY KEY,
            entry_id INTEGER NOT NULL,
            pos VARCHAR NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES dictionaryentry (id) ON DELETE CASCADE
        )
        """)
        
        # Create index on entry_id for faster lookups
        cursor.execute("CREATE INDEX idx_pos_entry_id ON part_of_speech (entry_id)")
        
        # 3. Create classifier table
        print("Creating classifier table...")
        cursor.execute("""
        CREATE TABLE classifier (
            id INTEGER PRIMARY KEY,
            entry_id INTEGER NOT NULL,
            classifier VARCHAR NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES dictionaryentry (id) ON DELETE CASCADE
        )
        """)
        
        # Create index on entry_id for faster lookups
        cursor.execute("CREATE INDEX idx_classifier_entry_id ON classifier (entry_id)")
        
        # 4. Create transcription table
        print("Creating transcription table...")
        cursor.execute("""
        CREATE TABLE transcription (
            id INTEGER PRIMARY KEY,
            entry_id INTEGER NOT NULL,
            system VARCHAR NOT NULL,
            value VARCHAR NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES dictionaryentry (id) ON DELETE CASCADE
        )
        """)
        
        # Create indexes for faster lookups
        cursor.execute("CREATE INDEX idx_transcription_entry_id ON transcription (entry_id)")
        cursor.execute("CREATE INDEX idx_transcription_system ON transcription (system)")
        
        # 5. Create meaning table
        print("Creating meaning table...")
        cursor.execute("""
        CREATE TABLE meaning (
            id INTEGER PRIMARY KEY,
            entry_id INTEGER NOT NULL,
            definition TEXT NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES dictionaryentry (id) ON DELETE CASCADE
        )
        """)
        
        # Create index on entry_id for faster lookups
        cursor.execute("CREATE INDEX idx_meaning_entry_id ON meaning (entry_id)")
        
        # Commit the transaction
        conn.commit()
        print("Database schema migration completed successfully!")
        
    except sqlite3.Error as e:
        # Roll back any changes if an error occurs
        if conn:
            conn.rollback()
        print(f"Database error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        # Roll back any changes if an error occurs
        if conn:
            conn.rollback()
        print(f"Error: {e}", file=sys.stderr)
        return False
    finally:
        # Close the connection
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)