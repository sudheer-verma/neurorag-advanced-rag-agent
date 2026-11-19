from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from app.schemas.documents import IngestRequest
from app.ingestion.document_loader import load_document


def create_document_router(pipeline, settings) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["documents"])
    records = {}
    pipeline.document_records = records

    @router.get("/documents")
    def documents():
        return list(records.values())

    @router.post("/ingest")
    def ingest(request: IngestRequest):
        if not request.text.strip():
            raise HTTPException(status_code=422, detail="Document text cannot be empty")
        result = pipeline.ingest(request.text, request.title, request.metadata)
        record = {
            "id": result["document_id"],
            "title": result["title"],
            "status": "indexed",
            "chunk_count": result["chunk_count"],
            "metadata": request.metadata,
        }
        records[record["id"]] = record
        return result

    @router.post("/documents/upload")
    async def upload(file: UploadFile = File(...)):
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".pdf", ".txt"}:
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
        content = await file.read()
        if not content:
            raise HTTPException(status_code=422, detail="Uploaded document is empty")
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        target = upload_dir / (file.filename or "upload")
        target.write_bytes(content)
        try:
            text = load_document(str(target))
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Unable to read document: {exc}") from exc
        if not text.strip():
            raise HTTPException(status_code=422, detail="Document contains no readable text")
        result = pipeline.ingest(text, Path(file.filename).stem, {"filename": file.filename})
        record = {
            "id": result["document_id"],
            "title": result["title"],
            "status": "indexed",
            "chunk_count": result["chunk_count"],
            "metadata": {"filename": file.filename},
        }
        records[record["id"]] = record
        return record

    @router.delete("/documents/{document_id}")
    def delete_document(document_id: str):
        if document_id not in records:
            raise HTTPException(status_code=404, detail="Document not found")
        pipeline.delete_document(document_id)
        del records[document_id]
        return {"deleted": True, "document_id": document_id}

    return router
