from pathlib import Path
from datetime import datetime
from bson import ObjectId

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pymongo.database import Database

from app.dependencies import get_db
from app.schemas import DocumentResponse, UploadResponse
from app.services.ocr import OCRUnavailableError
from app.services.pipeline import process_document
from app.services.storage import save_upload

router = APIRouter()


@router.delete("/documents/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(id: str, db: Database = Depends(get_db)) -> None:
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

    record = db.document_records.find_one({"_id": obj_id})
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Delete physical file
    stored_path = Path(record["stored_path"])
    if stored_path.exists():
        stored_path.unlink()

    # Delete from MongoDB
    db.document_records.delete_one({"_id": obj_id})


@router.post("/documents/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def upload_document(file: UploadFile = File(...), db: Database = Depends(get_db)) -> UploadResponse:
    stored_path = save_upload(file)
    try:
        result = process_document(stored_path)
    except OCRUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Processing failed: {exc}") from exc

    # Clean the raw text and fields for storage
    record_data = {
        "filename": file.filename or stored_path.name,
        "stored_path": str(stored_path),
        "document_type": result.document_type,
        "status": "processed",
        "extracted_data": result.fields,
        "validation_results": [v.model_dump() for v in result.validations],
        "raw_text": "\n".join(result.raw_lines),
        "created_at": datetime.utcnow(),
    }

    insert_result = db.document_records.insert_one(record_data)
    record_id = str(insert_result.inserted_id)

    return UploadResponse(
        id=record_id,
        filename=record_data["filename"],
        document_type=result.document_type,
        status=record_data["status"],
        extracted_data=result.fields,
        validation_results=result.validations,
        created_at=record_data["created_at"],
        raw_text=record_data["raw_text"],
    )


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(db: Database = Depends(get_db)) -> list[DocumentResponse]:
    records = db.document_records.find().sort("created_at", -1)
    
    docs = []
    for record in records:
        docs.append(
            DocumentResponse(
                id=str(record["_id"]),
                filename=record["filename"],
                document_type=record["document_type"],
                status=record["status"],
                extracted_data=record["extracted_data"],
                validation_results=record["validation_results"],
                created_at=record["created_at"],
                raw_text=record.get("raw_text"),
            )
        )
    return docs
