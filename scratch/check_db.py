import sqlite3
import json

db_path = r'e:\Abi(E)\New folder\strategic knights\2026-04-21-discussed-i-would-like-you-to\backend\identity_docs.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT * FROM document_records ORDER BY created_at DESC LIMIT 1")
row = cursor.fetchone()

if row:
    print(f"ID: {row['id']}")
    print(f"Filename: {row['filename']}")
    print(f"Created At: {row['created_at']}")
    print(f"Extracted JSON: {row['extracted_json']}")
    print(f"Raw Text: {row['raw_text']}")
else:
    print("No documents found.")

conn.close()
