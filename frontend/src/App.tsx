import { ChangeEvent, useEffect, useState } from "react";

type ValidationResult = {
  field: string;
  is_valid: boolean;
  message: string;
};

type DocumentRecord = {
  id: number;
  filename: string;
  document_type: "aadhaar" | "pan" | "driving_license" | "unknown";
  status: string;
  extracted_data: Record<string, unknown>;
  validation_results: ValidationResult[];
  created_at: string;
  raw_text?: string;
};

const API_BASE = "http://localhost:8000";

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [selected, setSelected] = useState<DocumentRecord | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadDocuments();
  }, []);

  async function loadDocuments() {
    try {
      const response = await fetch(`${API_BASE}/documents`);
      if (!response.ok) {
        throw new Error("Unable to load extracted documents");
      }
      const data = (await response.json()) as DocumentRecord[];
      setDocuments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
  }

  async function onUpload() {
    if (!file) {
      setError("Choose a document image before uploading.");
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const form = new FormData();
      form.append("file", file);

      const response = await fetch(`${API_BASE}/documents/upload`, {
        method: "POST",
        body: form
      });

      const data = (await response.json()) as DocumentRecord | { detail?: string };
      if (!response.ok) {
        throw new Error("detail" in data ? data.detail ?? "Upload failed" : "Upload failed");
      }

      const created = data as DocumentRecord;
      setDocuments((current) => [created, ...current]);
      setSelected(created);
      setFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  async function onDelete(id: string) {
    if (!window.confirm("Are you sure you want to delete this record? This cannot be undone.")) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/documents/${id}`, {
        method: "DELETE"
      });

      if (!response.ok) {
        throw new Error("Failed to delete record");
      }

      setDocuments((current) => current.filter((doc) => String(doc.id) !== id));
      if (String(selected?.id) === id) {
        setSelected(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">OCR + ML Extraction</p>
          <h1>Identity document ingestion for Aadhaar, PAN, and driving licenses</h1>
          <p className="lede">
            Upload an identity card image and review the extracted structured JSON, validation checks,
            and OCR-derived text in one place.
          </p>
        </div>
        <div className="upload-card">
          <label className="upload-label" htmlFor="document">
            Select image
          </label>
          <input id="document" type="file" accept="image/png,image/jpeg,image/webp,application/pdf" onChange={onFileChange} />
          <button className="primary-button" onClick={onUpload} disabled={isUploading}>
            {isUploading ? "Processing..." : "Upload and extract"}
          </button>
          {file ? <p className="hint">Ready: {file.name}</p> : <p className="hint">PNG, JPG, JPEG, WEBP up to 10 MB</p>}
          {error ? <p className="error">{error}</p> : null}
        </div>
      </section>

      <section className="content-grid">
        <aside className="history-panel">
          <div className="panel-header">
            <h2>Processed documents</h2>
            <button className="ghost-button" onClick={() => void loadDocuments()}>
              Refresh
            </button>
          </div>
          <div className="document-list">
            {documents.length === 0 ? <p className="empty">No documents processed yet.</p> : null}
            {documents.map((doc) => (
              <button
                key={doc.id}
                className={`document-card ${selected?.id === doc.id ? "selected" : ""}`}
                onClick={() => setSelected(doc)}
              >
                <span className="doc-type">{formatDocumentType(doc.document_type)}</span>
                <strong>{doc.filename}</strong>
                {/*<span className="timestamp">{new Date(doc.created_at).toLocaleString()}</span>*/}
              </button>
            ))}
          </div>
        </aside>

        <section className="results-panel">
          {selected ? (
            <>
              <div className="panel-header">
                <div>
                  <p className="eyebrow">Selected record</p>
                  <h2>{selected.filename}</h2>
                </div>
                <div className="panel-actions">
                  <span className="status-pill">{formatDocumentType(selected.document_type)}</span>
                  <button className="danger-button" onClick={() => void onDelete(String(selected.id))}>
                    Delete Record
                  </button>
                </div>
              </div>

              <div className="metrics-grid">
                <article className="metric-card">
                  <h3>Structured JSON</h3>
                  <pre>{JSON.stringify(selected.extracted_data, null, 2)}</pre>
                </article>

                <article className="metric-card">
                  <h3>Validation checks</h3>
                  <ul className="validation-list">
                    {selected.validation_results.length === 0 ? <li>No validation results available.</li> : null}
                    {selected.validation_results.map((item) => (
                      <li key={`${item.field}-${item.message}`} className={item.is_valid ? "valid" : "invalid"}>
                        <strong>{item.field}</strong> {item.message}
                      </li>
                    ))}
                  </ul>
                </article>
              </div>

              <article className="raw-text-card">
                <h3>Raw OCR text</h3>
                <pre>{selected.raw_text ?? "Raw text is only included for newly uploaded records in this session."}</pre>
              </article>
            </>
          ) : (
            <div className="empty-state">
              <h2>No selection yet</h2>
              <p>Upload a document to see extraction results.</p>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

function formatDocumentType(value: DocumentRecord["document_type"]) {
  return value.replace("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}
