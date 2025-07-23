# HSK Level and Frequency Rank Database Update

## Overview

This document describes the process of updating the Chinese dictionary database (`cedict.db`) with HSK level and frequency rank data from the `complete.json` file.

## Database Changes

The database already had the necessary columns in the `dictionaryentry` table:
- `hsk_level`: An integer representing the HSK (Hanyu Shuiping Kaoshi) level of the word
- `frequency_rank`: An integer representing the frequency rank of the word (lower numbers indicate more frequent usage)

No schema changes were required; we only needed to populate these existing columns with data from the `complete.json` file.

## Data Source

The `complete.json` file contains a comprehensive list of Chinese words with various attributes, including:
- `simplified`: The simplified Chinese character(s)
- `traditional`: The traditional Chinese character(s)
- `level`: An array containing HSK level information (e.g., "new-4", "old-3", "new-7+")
- `frequency`: A numeric value representing the frequency rank

## Implementation

A Python script (`update_hsk_frequency.py`) was created to:
1. Parse the `complete.json` file
2. Connect to the `cedict.db` SQLite database
3. Match entries from the JSON file to entries in the database
4. Update the `hsk_level` and `frequency_rank` columns for matching entries

### HSK Level Conversion

The HSK level in the JSON file is represented as an array with values like "new-4" (new HSK system, level 4) or "old-3" (old HSK system, level 3). The script prioritizes the new HSK system and falls back to the old system if needed. For entries with "new-7+", the script uses 7 as the level.

### Results

The script successfully updated the database with:
- 11,882 entries now having HSK level data
- 11,882 entries now having frequency rank data

Out of 11,494 entries in the `complete.json` file, matches were found for 12,621 database entries (the difference is due to multiple traditional forms for some simplified characters). Only 34 entries from the JSON file couldn't be matched to database entries.

## Verification

The implementation was verified by running the `test_search_logic.py` script, which confirmed that the HSK level and frequency rank data is correctly accessible through the API. Examples of entries with HSK level and frequency rank data:
- '中' (zhong4): HSK Level 1, Frequency Rank 71
- '这' (zhei4): HSK Level 1, Frequency Rank 11
- '中国' (Zhong1 guo2): HSK Level 1, Frequency Rank 729

Not all entries in the database have HSK level and frequency rank data, as the `complete.json` file doesn't contain data for all entries in the database.

## Future Improvements

Potential future improvements could include:
1. Finding additional sources of HSK level and frequency data to cover more entries in the database
2. Adding a way to filter or sort search results by HSK level or frequency rank
3. Implementing a feature to show only words within a specific HSK level range