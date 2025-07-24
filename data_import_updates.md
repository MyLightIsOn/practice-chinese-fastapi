# Data Import Script Updates Documentation

This document describes the updates made to the data import script (`update_hsk_frequency.py`) for the Chinese dictionary enhancement project.

## Overview

The data import script has been updated to handle the enhanced database schema, including:
- Separating old and new HSK levels
- Adding radical information
- Adding parts of speech
- Adding classifiers
- Adding multiple transcription systems
- Adding multiple meanings/definitions

## Changes to Extraction Functions

### HSK Level Extraction

The original `extract_hsk_level` function has been replaced with `extract_hsk_levels`, which now returns both old and new HSK levels separately:

```python
def extract_hsk_levels(level_array):
    """
    Extract both old and new HSK levels from the level array.
    For 'new-7+', return 7 for new HSK level.
    Returns a tuple of (old_hsk_level, new_hsk_level).
    """
```

### New Extraction Functions

Several new functions have been added to extract additional data from the JSON:

1. `extract_radical(entry)`: Extracts the radical component of the character
2. `extract_pos(entry)`: Extracts parts of speech
3. `extract_classifiers(form)`: Extracts classifiers
4. `extract_transcriptions(form)`: Extracts transcriptions from different systems
5. `extract_meanings(form)`: Extracts multiple meanings/definitions

## Changes to Database Update Logic

### Data Collection

The script now collects data for multiple tables:
- Main updates for the `dictionaryentry` table
- Parts of speech for the `part_of_speech` table
- Classifiers for the `classifier` table
- Transcriptions for the `transcription` table
- Meanings for the `meaning` table

### Transaction Handling

The script now uses proper transaction handling:
- All database operations are wrapped in a transaction
- Error handling with rollback in case of exceptions
- Verification of updates with counts of inserted data

### Batch Processing

The script processes updates in batches for better performance and memory usage:
- Main table updates are processed in batches of 1000
- Related table inserts are processed in batches of 1000

## Data Migration

The script handles data migration from the existing schema to the new schema:
- Existing HSK level data is migrated to old_hsk_level and new_hsk_level columns
- The original hsk_level column is maintained for backward compatibility
- Existing data in related tables is cleared before inserting new data

## Verification

The script verifies the updates by counting:
- Entries with old HSK level
- Entries with new HSK level
- Entries with radical information
- Total parts of speech
- Total classifiers
- Total transcriptions
- Total meanings

## Next Steps

After this data import update, the next steps will be:
1. Update the API response format to include the new data
2. Optimize performance for queries involving the new tables
3. Update tests and documentation