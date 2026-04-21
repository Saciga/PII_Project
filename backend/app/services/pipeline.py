from __future__ import annotations

from pathlib import Path

from app.schemas import ExtractedDocument
from app.services.extractors import extract_document
from app.services.ocr import run_ocr
from app.services.preprocessing import preprocess_image


def process_document(path: Path) -> ExtractedDocument:
    preprocessed = preprocess_image(path)
    ocr_lines = run_ocr(preprocessed.image)
    extracted = extract_document(ocr_lines)
    extracted.fields["preprocessing_steps"] = preprocessed.debug_steps
    return extracted
