from __future__ import annotations

import re
from statistics import mean

from rapidfuzz import fuzz

from app.schemas import ExtractedDocument
from app.services.validators import (
    AADHAAR_RE,
    DL_RE,
    PAN_RE,
    validate_aadhaar,
    validate_date,
    validate_driving_license,
    validate_pan,
)


DATE_RE = re.compile(r"\d{2}[\/\-.]\d{2}[\/\-.]\d{2,4}")


def classify_document(lines: list[str]) -> str:
    joined = " ".join(lines).upper()
    candidates = {
        "aadhaar": max(
            fuzz.partial_ratio(joined, "GOVERNMENT OF INDIA"),
            fuzz.partial_ratio(joined, "AADHAAR"),
            100 if AADHAAR_RE.search(joined) else 0,
        ),
        "pan": max(
            fuzz.partial_ratio(joined, "INCOME TAX DEPARTMENT"),
            fuzz.partial_ratio(joined, "PERMANENT ACCOUNT NUMBER"),
            100 if PAN_RE.search(joined) else 0,
        ),
        "driving_license": max(
            fuzz.partial_ratio(joined, "DRIVING LICENCE"),
            fuzz.partial_ratio(joined, "DRIVING LICENSE"),
            100 if DL_RE.search(joined) else 0,
        ),
    }
    document_type, score = max(candidates.items(), key=lambda item: item[1])
    return document_type if score >= 60 else "unknown"


def extract_document(ocr_lines: list[dict[str, object]]) -> ExtractedDocument:
    texts = [str(line["text"]).strip() for line in ocr_lines if str(line["text"]).strip()]
    confidences = [float(line["confidence"]) for line in ocr_lines if line.get("confidence") is not None]
    document_type = classify_document(texts)

    if document_type == "aadhaar":
        return extract_aadhaar(texts, confidences)
    if document_type == "pan":
        return extract_pan(texts, confidences)
    if document_type == "driving_license":
        return extract_driving_license(texts, confidences)

    return ExtractedDocument(
        document_type="unknown",
        fields={"message": "Unable to confidently classify document"},
        confidence=round(mean(confidences), 4) if confidences else 0.0,
        raw_lines=texts,
        validations=[],
    )


def extract_aadhaar(lines: list[str], confidences: list[float]) -> ExtractedDocument:
    print(f"DEBUG: Lines to extract from: {lines}")
    aadhaar_number = find_first(AADHAAR_RE, lines, normalize_spaces=True)
    dob = extract_value_after_keywords(lines, ["DOB", "D0B", "Year of Birth", "YOB"]) or find_first(DATE_RE, lines)
    gender = find_value_from_list(lines, ["MALE", "FEMALE", "TRANSGENDER"])
    name = infer_name(lines, forbidden=["GOVERNMENT OF INDIA", "AADHAAR", "DOB", "D0B", "MALE", "FEMALE"])
    print(f"DEBUG: Extracted raw values -> Name: {name}, DOB: {dob}, Gender: {gender}")
    validations = [
        validate_aadhaar(aadhaar_number),
        validate_date("date_of_birth", dob),
    ]
    return ExtractedDocument(
        document_type="aadhaar",
        fields={
            "name": name,
            "aadhaar_number": compact_numeric(aadhaar_number),
            "date_of_birth": dob,
            "gender": gender.title() if gender else None,
        },
        confidence=round(mean(confidences), 4) if confidences else 0.0,
        raw_lines=lines,
        validations=validations,
    )


def extract_pan(lines: list[str], confidences: list[float]) -> ExtractedDocument:
    pan_number = find_first(PAN_RE, lines)
    dob = find_first(DATE_RE, lines)
    name = infer_name(lines, forbidden=["INCOME TAX DEPARTMENT", "PERMANENT ACCOUNT NUMBER", "GOVT OF INDIA"])
    father_name = infer_secondary_name(lines, anchor=name)
    validations = [
        validate_pan(pan_number),
        validate_date("date_of_birth", dob),
    ]
    return ExtractedDocument(
        document_type="pan",
        fields={
            "name": name,
            "father_name": father_name,
            "pan_number": pan_number,
            "date_of_birth": dob,
        },
        confidence=round(mean(confidences), 4) if confidences else 0.0,
        raw_lines=lines,
        validations=validations,
    )


def extract_driving_license(lines: list[str], confidences: list[float]) -> ExtractedDocument:
    license_number = find_first(DL_RE, lines, normalize_spaces=True)
    dates = [match.group(0) for line in lines for match in DATE_RE.finditer(line)]
    name = infer_name(lines, forbidden=["DRIVING LICENCE", "DRIVING LICENSE", "INDIA", "TRANSPORT"])
    validations = [
        validate_driving_license(license_number),
        validate_date("date_of_birth", dates[0] if dates else None),
    ]
    return ExtractedDocument(
        document_type="driving_license",
        fields={
            "name": name,
            "license_number": re.sub(r"\s+", "", license_number) if license_number else None,
            "date_of_birth": dates[0] if dates else None,
            "valid_till": dates[-1] if len(dates) > 1 else None,
        },
        confidence=round(mean(confidences), 4) if confidences else 0.0,
        raw_lines=lines,
        validations=validations,
    )


def find_first(pattern: re.Pattern[str], lines: list[str], normalize_spaces: bool = False) -> str | None:
    for line in lines:
        match = pattern.search(line.upper())
        if match:
            value = match.group(0)
            return re.sub(r"\s+", "", value) if normalize_spaces else value
    return None


def extract_value_after_keywords(lines: list[str], keywords: list[str]) -> str | None:
    for line in lines:
        for keyword in keywords:
            if keyword.upper() in line.upper():
                dates = DATE_RE.findall(line)
                if dates:
                    return dates[0]
                parts = re.split(r":|-", line, maxsplit=1)
                if len(parts) == 2:
                    return parts[1].strip()
    return None


def find_value_from_list(lines: list[str], values: list[str]) -> str | None:
    for value in values:
        for line in lines:
            if value in line.upper():
                return value
    return None


def infer_name(lines: list[str], forbidden: list[str]) -> str | None:
    for line in lines:
        cleaned = line.strip()
        upper = cleaned.upper()
        if any(token in upper for token in forbidden):
            continue
        if DATE_RE.search(upper) or AADHAAR_RE.search(upper) or PAN_RE.search(upper) or DL_RE.search(upper):
            continue
        if (1 <= len(cleaned.split()) <= 4) and cleaned.replace(" ", "").isalpha() and len(cleaned) > 3:
            print(f"DEBUG: Found candidate name: {cleaned}")
            return cleaned.title()
        else:
            print(f"DEBUG: Line '{cleaned}' rejected (split count: {len(cleaned.split())}, isalpha: {cleaned.replace(' ', '').isalpha()}, length: {len(cleaned)})")
    return None


def infer_secondary_name(lines: list[str], anchor: str | None) -> str | None:
    if not anchor:
        return None
    seen_anchor = False
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        if anchor.lower() == cleaned.lower():
            seen_anchor = True
            continue
        if seen_anchor and cleaned.replace(" ", "").isalpha() and 2 <= len(cleaned.split()) <= 4:
            return cleaned.title()
    return None


def compact_numeric(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\D", "", value)
