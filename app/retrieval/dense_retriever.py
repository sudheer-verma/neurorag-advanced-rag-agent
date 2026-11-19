import hashlib
import math
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


class LocalDenseEmbeddings:
    dimensions = 128

    def embed(self, text: str) -> List[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode()).digest()
            for i in range(self.dimensions):
                vector[i] += (digest[i % len(digest)] - 128) / 128.0
        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector] if norm else vector


class DenseRetriever:
    def __init__(self, path: str, embeddings: LocalDenseEmbeddings | None = None):
        self.client = QdrantClient(path=path)
        self.embeddings = embeddings or LocalDenseEmbeddings()
        self.collection = "neurorag_children"
        try:
            self.client.get_collection(self.collection)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.embeddings.dimensions, distance=Distance.COSINE),
            )

    def index(self, documents: List[dict]) -> int:
        if not documents:
            return 0
        points = [
            PointStruct(id=abs(hash(doc["id"])) % (2**63 - 1),
                        vector=self.embeddings.embed(doc["text"]),
                        payload=doc)
            for doc in documents
        ]
        self.client.upsert(collection_name=self.collection, points=points)
        return len(points)

    def search(self, query: str, top_k: int = 20) -> List[dict]:
        vector = self.embeddings.embed(query)
        hits = self.client.query_points(
            collection_name=self.collection,
            query=vector,
            limit=top_k,
            with_payload=True,
        ).points
        return [dict(hit.payload or {}) for hit in hits]

    def scroll(self, limit: int = 10000) -> List[dict]:
        points, _ = self.client.scroll(
            collection_name=self.collection,
            limit=limit,
            with_payload=True,
        )
        return [dict(point.payload or {}) for point in points]

    def delete_document(self, document_id: str) -> int:
        documents = self.scroll()
        ids = [
            abs(hash(doc["id"])) % (2**63 - 1)
            for doc in documents
            if doc.get("document_id") == document_id
        ]
        if ids:
            self.client.delete(collection_name=self.collection, points_selector=ids)
        return len(ids)
