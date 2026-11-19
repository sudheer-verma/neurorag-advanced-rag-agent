import time
from typing import List


class LocalReranker:
    def rerank(self, query: str, documents: List[dict], top_k: int = 5, threshold: float = 0.25):
        query_terms = set(query.lower().split())
        ranked = []
        for document in documents:
            text = document.get("text", "").lower()
            terms = set(text.split())
            overlap = len(query_terms.intersection(terms))
            score = overlap / max(len(query_terms), 1)
            ranked.append((score, document))
        ranked.sort(key=lambda item: (-item[0], item[1].get("id", "")))
        output = []
        for score, document in ranked[:top_k]:
            if score >= threshold:
                item = dict(document)
                item["rerank_score"] = round(score, 6)
                item["rerank_provider"] = "local"
                output.append(item)
        return output


class CohereReranker:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def rerank(self, query: str, documents: List[dict], top_k: int = 5, threshold: float = 0.25):
        import cohere
        client = cohere.ClientV2(api_key=self.api_key)
        response = client.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=[doc["text"] for doc in documents[:20]],
            top_n=top_k,
        )
        output = []
        for result in response.results:
            document = dict(documents[result.index])
            score = float(result.relevance_score)
            if score >= threshold:
                document["rerank_score"] = score
                document["rerank_provider"] = "cohere"
                output.append(document)
        return output


class Reranker:
    def __init__(self, provider: str = "local", api_key: str = "", threshold: float = 0.25):
        self.provider = provider if provider == "cohere" and api_key else "local"
        self.threshold = threshold
        self.engine = CohereReranker(api_key) if self.provider == "cohere" else LocalReranker()

    def rerank(self, query: str, documents: List[dict]):
        start = time.perf_counter()
        try:
            result = self.engine.rerank(query, documents[:20], top_k=5, threshold=self.threshold)
        except Exception:
            result = LocalReranker().rerank(query, documents[:20], top_k=5, threshold=self.threshold)
        latency_ms = (time.perf_counter() - start) * 1000
        return result, latency_ms
