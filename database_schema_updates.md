# Database Schema Updates Documentation

This document describes the database schema updates implemented for the Chinese dictionary enhancement project.

## Overview

The database schema has been updated to support more detailed Chinese character data, including:
- Radical information
- Separate old and new HSK levels
- Parts of speech
- Classifiers
- Multiple transcription systems
- Multiple meanings/definitions

## Changes to Existing Tables

### DictionaryEntry Table

The following columns have been added to the `dictionaryentry` table:

| Column | Type | Description |
|--------|------|-------------|
| `radical` | VARCHAR | The radical component of the character |
| `old_hsk_level` | INTEGER | The HSK level in the old system (1-6) |
| `new_hsk_level` | INTEGER | The HSK level in the new system (1-7+) |

The existing `hsk_level` column is retained for backward compatibility.

## New Tables

### Part of Speech Table

A new `part_of_speech` table has been created to store multiple parts of speech for each dictionary entry:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `entry_id` | INTEGER | Foreign key to dictionaryentry.id |
| `pos` | VARCHAR | Part of speech code (e.g., "n" for noun, "v" for verb) |

An index has been created on `entry_id` for faster lookups.

### Classifier Table

A new `classifier` table has been created to store multiple classifiers for each dictionary entry:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `entry_id` | INTEGER | Foreign key to dictionaryentry.id |
| `classifier` | VARCHAR | The classifier character(s) |

An index has been created on `entry_id` for faster lookups.

### Transcription Table

A new `transcription` table has been created to store multiple transcription systems for each dictionary entry:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `entry_id` | INTEGER | Foreign key to dictionaryentry.id |
| `system` | VARCHAR | The transcription system (e.g., "pinyin", "numeric", "wadegiles", "bopomofo", "romatzyh") |
| `value` | VARCHAR | The transcription value |

Indexes have been created on `entry_id` and `system` for faster lookups.

### Meaning Table

A new `meaning` table has been created to store multiple meanings/definitions for each dictionary entry:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `entry_id` | INTEGER | Foreign key to dictionaryentry.id |
| `definition` | TEXT | The English definition |

An index has been created on `entry_id` for faster lookups.

## Foreign Key Constraints

All new tables have foreign key constraints on `entry_id` referencing `dictionaryentry.id` with `ON DELETE CASCADE`. This ensures that if a dictionary entry is deleted, all related records in the new tables will also be deleted.

## Indexes

The following indexes have been created for performance optimization:

| Index | Table | Column(s) |
|-------|-------|-----------|
| `idx_pos_entry_id` | `part_of_speech` | `entry_id` |
| `idx_classifier_entry_id` | `classifier` | `entry_id` |
| `idx_transcription_entry_id` | `transcription` | `entry_id` |
| `idx_transcription_system` | `transcription` | `system` |
| `idx_meaning_entry_id` | `meaning` | `entry_id` |

## Data Migration

The schema update does not include data migration. The existing data in the `hsk_level` column will remain unchanged. Data migration to populate the new columns and tables will be handled by the data import script in a separate update.

## Backward Compatibility

The schema updates are designed to be backward compatible with existing code. The original columns in the `dictionaryentry` table remain unchanged, and the existing queries should continue to work as before.

## Next Steps

After this schema update, the next steps will be:
1. Update the data import script to populate the new columns and tables
2. Update the API response format to include the new data
3. Optimize performance for queries involving the new tables
4. Update tests and documentation