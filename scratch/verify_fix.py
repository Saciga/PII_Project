import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.extractors import extract_aadhaar

ocr_text = [
    "ART 3T4R, AT 96q",
    "89748366 8695",
    "60T/Male",
    "m/D0B19/05/2004",
    "ABITHMR",
    "9g LT IJT",
    "HRHR"
]
confidences = [0.9] * len(ocr_text)

result = extract_aadhaar(ocr_text, confidences)

print(f"Document Type: {result.document_type}")
print(f"Name: {result.fields.get('name')}")
print(f"Aadhaar: {result.fields.get('aadhaar_number')}")
print(f"DOB: {result.fields.get('date_of_birth')}")
print(f"Gender: {result.fields.get('gender')}")

# Validation checks
for v in result.validations:
    print(f"Validation {v.field}: {v.is_valid} ({v.message})")
