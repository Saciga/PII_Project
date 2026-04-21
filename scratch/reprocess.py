import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.pipeline import process_document

# Path to the last uploaded file (from DB check)
file_path = Path(r'e:\Abi(E)\New folder\strategic knights\2026-04-21-discussed-i-would-like-you-to\uploads\1bfce48bcac441959221f557d174e02f.pdf')

if not file_path.exists():
    print(f"File not found: {file_path}")
    sys.exit(1)

print(f"Processing: {file_path}")
result = process_document(file_path)

print(f"\nFinal Result:")
print(f"Name: {result.fields.get('name')}")
print(f"DOB: {result.fields.get('date_of_birth')}")
print(f"Aadhaar: {result.fields.get('aadhaar_number')}")
