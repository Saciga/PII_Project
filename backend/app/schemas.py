from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


DocumentType = Literal["aadhaar", "pan", "driving_license", "unknown"]


class ValidationResult(BaseModel):
    field: str
    is_valid: bool
    message: str


class ExtractedDocument(BaseModel):
    document_type: DocumentType
    fields: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    raw_lines: list[str] = Field(default_factory=list)
    validations: list[ValidationResult] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    id: str
    filename: str
    document_type: DocumentType
    status: str
    extracted_data: dict[str, Any]
    validation_results: list[ValidationResult]
    created_at: datetime
    raw_text: str | None = None


class UploadResponse(DocumentResponse):
    raw_text: str
