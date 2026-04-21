from __future__ import annotations

import re
from datetime import datetime

from app.schemas import ValidationResult


AADHAAR_RE = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
PAN_RE = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
DL_RE = re.compile(r"\b[A-Z]{2}[0-9]{2}\s?[0-9]{4,11}\b")


def validate_aadhaar(value: str | None) -> ValidationResult:
    if not value:
        return ValidationResult(field="aadhaar_number", is_valid=False, message="Missing Aadhaar number")
    normalized = re.sub(r"\s+", "", value)
    ok = bool(re.fullmatch(r"\d{12}", normalized))
    return ValidationResult(
        field="aadhaar_number",
        is_valid=ok,
        message="Valid Aadhaar format" if ok else "Aadhaar number must contain exactly 12 digits",
    )


def validate_pan(value: str | None) -> ValidationResult:
    if not value:
        return ValidationResult(field="pan_number", is_valid=False, message="Missing PAN number")
    ok = bool(PAN_RE.fullmatch(value.upper()))
    return ValidationResult(
        field="pan_number",
        is_valid=ok,
        message="Valid PAN format" if ok else "PAN must match AAAAA9999A format",
    )


def validate_driving_license(value: str | None) -> ValidationResult:
    if not value:
        return ValidationResult(field="license_number", is_valid=False, message="Missing driving license number")
    compact = re.sub(r"\s+", "", value.upper())
    ok = bool(re.fullmatch(r"[A-Z]{2}[0-9]{2}[0-9]{4,11}", compact))
    return ValidationResult(
        field="license_number",
        is_valid=ok,
        message="Valid driving license format" if ok else "Driving license format looks invalid",
    )


def validate_date(field: str, value: str | None) -> ValidationResult:
    if not value:
        return ValidationResult(field=field, is_valid=False, message=f"Missing {field.replace('_', ' ')}")

    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d/%m/%y"):
        try:
            datetime.strptime(value, fmt)
            return ValidationResult(field=field, is_valid=True, message="Valid date")
        except ValueError:
            continue
    return ValidationResult(field=field, is_valid=False, message="Date must be in DD/MM/YYYY-style format")
