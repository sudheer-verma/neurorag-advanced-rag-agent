from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.responses import JSONResponse
from pathlib import Path
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.retrieval.dense_retriever import DenseRetriever
from app.retrieval.sparse_retriever import SparseRetriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.ingestion.ingestion_pipeline import IngestionPipeline
from app.compression.reranker import Reranker
from app.memory.memory_manager import MemoryManager
from app.memory.persona_manager import PersonaManager
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.telemetry import TelemetryStore
from app.api.chat import create_chat_router
from app.api.documents import create_document_router
from app.api.memories import create_memory_router


settings = get_settings()
logger = configure_logging()
dense = DenseRetriever(settings.qdrant_path)
sparse = SparseRetriever()
pipeline = IngestionPipeline(dense, sparse)
memory = MemoryManager(settings.memory_db_path)
persona = PersonaManager()
reranker = Reranker(settings.rerank_provider, settings.cohere_api_key, settings.rerank_threshold)
llm = LLMService(settings.llm_provider, settings.openai_api_key)
telemetry = TelemetryStore(settings.telemetry_db_path)
hybrid = HybridRetriever(dense, sparse, pipeline.parents, pipeline.mapping)
rag_service = RAGService(hybrid, memory, persona, reranker, llm)
root = Path(__file__).resolve().parents[1]


@asynccontextmanager
async def lifespan(app: FastAPI):
    restore_index()
    yield


app = FastAPI(
    title="NeuroRAG",
    description="Advanced RAG Agent with hybrid retrieval, reranking, context compression, and semantic memory",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.cors_origins == "*" else [item.strip() for item in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=422,
        content={"error": "invalid_request", "detail": str(exc), "path": str(request.url.path)},
    )

app.include_router(create_chat_router(rag_service, telemetry))
app.include_router(create_document_router(pipeline, settings))
app.include_router(create_memory_router(memory))


def restore_index():
    restored = dense.scroll()
    if restored:
        pipeline.children.extend(restored)
        for child in restored:
            parent_id = child.get("parent_id")
            if parent_id and parent_id not in pipeline.parents:
                pipeline.parents[parent_id] = {
                    "id": parent_id,
                    "document_id": child.get("document_id"),
                    "title": child.get("title", "Document"),
                    "text": child.get("parent_text", child.get("text", "")),
                }
            pipeline.mapping[child["id"]] = parent_id
        sparse.index_documents(pipeline.children)
    if not pipeline.children:
        sample_dir = root / "data" / "sample_documents"
        for sample_path in sorted(sample_dir.glob("*")):
            if sample_path.suffix.lower() in {".txt", ".pdf"}:
                try:
                    from app.ingestion.document_loader import load_document
                    text = load_document(str(sample_path))
                    if text.strip():
                        pipeline.ingest(text, sample_path.stem, {"filename": sample_path.name})
                except Exception as exc:
                    logger.error("Failed to ingest sample document %s: %s", sample_path.name, exc)


@app.get("/health")
def health():
    rerank_provider = "cohere" if reranker.provider == "cohere" else "local"
    llm_provider = "openai" if llm.provider == "openai" else "local"
    return {
        "status": "ok",
        "service": "NeuroRAG",
        "environment": "local" if llm_provider == "local" and rerank_provider == "local" else "configured",
        "providers": {
            "llm": llm_provider,
            "embedding": "local",
            "rerank": rerank_provider,
            "memory": "sqlite",
            "vector": "qdrant-local",
        },
    }


@app.get("/api/status")
def status():
    return {
        "health": health(),
        "documents": len(pipeline.children),
        "parents": len(pipeline.parents),
        "telemetry": telemetry.summary(),
    }


frontend = root / "frontend"
if frontend.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend / "assets")), name="assets")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    index = frontend / "index.html"
    if not index.exists():
        return HTMLResponse("<h1>NeuroRAG</h1>", status_code=200)
    return HTMLResponse(index.read_text(encoding="utf-8"))
