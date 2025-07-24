# Data Import Script Instructions

## Overview

The data import script (`update_hsk_frequency.py`) has been updated to handle the enhanced database schema for the Chinese dictionary. This document provides instructions for running the script and verifying the results.

## Changes Made

The script has been updated to:

1. Extract and store radical information
2. Separate old and new HSK levels
3. Store parts of speech in the `part_of_speech` table
4. Store classifiers in the `classifier` table
5. Store transcriptions in the `transcription` table
6. Store meanings in the `meaning` table

For detailed information about the changes, see `data_import_updates.md`.

## Prerequisites

Before running the script, ensure that:

1. The database schema has been updated using the `db_schema_migration.py` script
2. The `complete.json` file is in the project root directory
3. Python 3.6 or higher is installed

## Running the Script

To run the script:

```bash
python update_hsk_frequency.py
```

The script will:

1. Load data from `complete.json`
2. Match entries with existing records in the database
3. Update the `dictionaryentry` table with radical, old_hsk_level, new_hsk_level, and frequency_rank
4. Insert parts of speech into the `part_of_speech` table
5. Insert classifiers into the `classifier` table
6. Insert transcriptions into the `transcription` table
7. Insert meanings into the `meaning` table

## Testing with a Subset of Data

If you want to test the script with a small subset of data before running the full update, you can use the `test_update_script.py` script:

```bash
python test_update_script.py
```

This script processes only the first 10 entries from `complete.json` and provides detailed output about what data is being extracted and inserted.

## Verifying the Results

After running the script, you can verify the results by checking the counts of records in each table:

```sql
SELECT COUNT(*) FROM dictionaryentry WHERE old_hsk_level IS NOT NULL;
SELECT COUNT(*) FROM dictionaryentry WHERE new_hsk_level IS NOT NULL;
SELECT COUNT(*) FROM dictionaryentry WHERE radical IS NOT NULL;
SELECT COUNT(*) FROM part_of_speech;
SELECT COUNT(*) FROM classifier;
SELECT COUNT(*) FROM transcription;
SELECT COUNT(*) FROM meaning;
```

You can also check specific entries to verify that the data was imported correctly:

```sql
SELECT d.simplified, d.traditional, d.radical, d.old_hsk_level, d.new_hsk_level, 
       p.pos, c.classifier, t.system, t.value, m.definition
FROM dictionaryentry d
LEFT JOIN part_of_speech p ON d.id = p.entry_id
LEFT JOIN classifier c ON d.id = c.entry_id
LEFT JOIN transcription t ON d.id = t.entry_id
LEFT JOIN meaning m ON d.id = m.entry_id
WHERE d.simplified = '你好'
LIMIT 10;
```

## Troubleshooting

If you encounter any issues:

1. Check that the database schema has been updated correctly
2. Verify that the `complete.json` file is in the correct format
3. Check the error messages for specific issues
4. If the script fails, the transaction will be rolled back, so you can safely run it again after fixing the issues

## Next Steps

After successfully running the data import script, the next steps are:

1. Update the API response format to include the new data
2. Optimize performance for queries involving the new tables
3. Update tests and documentation