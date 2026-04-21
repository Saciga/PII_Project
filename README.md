# Identity Document PII Extractor

Full-stack application for uploading Indian identity documents, extracting PII with an open-source OCR pipeline, validating the extracted fields, and storing structured JSON output in a database.

## Stack

- Backend: FastAPI, SQLAlchemy, SQLite
- OCR / ML: PaddleOCR, OpenCV, Pillow, NumPy
- Frontend: React, TypeScript, Vite
- Storage: SQLite by default, replaceable with PostgreSQL

## Python version

- Use Python `3.10` or `3.11` for the backend.
- The current PaddleOCR / PaddlePaddle stack is not reliable on Python `3.13` in this project setup.

## Supported documents

- Aadhaar card
- PAN card
- Driving license

## Features

- Upload identity document images
- Image preprocessing for denoising, contrast enhancement, rotation correction, and perspective normalization
- OCR using open-source models only
- Rule-based document classification plus structured field extraction
- Field validation for Aadhaar, PAN, dates, and driving license numbers
- JSON result persistence in a database
- Frontend review screen showing extracted data and validation status

## Project layout

```text
backend/
frontend/
uploads/
```

## Quick start

### Backend

```powershell
cd backend
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Notes

- The backend stores uploaded files locally in `uploads/`.
- For production, move to object storage and switch to PostgreSQL.
- The current extractor uses OCR plus document-specific parsing and validation. The codebase is structured so a fine-tuned LayoutLM / Donut-style model can be plugged in later under `backend/app/services`.
- `paddleocr==2.8.1` requires `numpy<2`, so the backend pins `numpy==1.26.4`.
