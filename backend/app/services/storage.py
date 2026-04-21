from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def save_upload(file: UploadFile) -> Path:
    suffix = Path(file.filename or "").suffix.lower().lstrip(".")
    if suffix not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: .{suffix or 'unknown'}",
        )

    safe_name = f"{uuid4().hex}.{suffix}"
    destination = settings.upload_dir / safe_name
    content = file.file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds {settings.max_upload_size_mb} MB limit",
        )

    destination.write_bytes(content)
    return destination
