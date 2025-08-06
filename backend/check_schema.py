#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('apex_ade.db')
cursor = conn.cursor()

# Get table info
cursor.execute("PRAGMA table_info(documents)")
columns = cursor.fetchall()

print("Documents table columns:")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

# Check if archived columns exist
column_names = [col[1] for col in columns]
print(f"\nArchived column exists: {'archived' in column_names}")
print(f"Archived_at column exists: {'archived_at' in column_names}")
print(f"Archived_by column exists: {'archived_by' in column_names}")

conn.close()