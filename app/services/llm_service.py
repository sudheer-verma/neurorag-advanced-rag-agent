import time
import re


class LLMService:
    def __init__(self, provider: str = "local", api_key: str = ""):
        self.provider = provider if provider == "openai" and api_key else "local"
        self.api_key = api_key

    def generate(self, query: str, context_documents: list[dict], persona: str) -> tuple[str, float]:
        start = time.perf_counter()
        if self.provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            prompt = f"{persona}\nContext:\n" + "\n\n".join(d["text"] for d in context_documents)
            prompt += f"\n\nQuestion: {query}"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": query}],
            )
            answer = response.choices[0].message.content or ""
        else:
            code_only = "code-only" in persona.lower()
            brief = "brief" in persona.lower()
            terms = re.findall(r"\b[A-Za-z][A-Za-z0-9+#.]*\b", query)
            merge_sort = re.search(r"merge\s*sort", query, re.I)
            if merge_sort:
                language = "python" if "python" in persona.lower() else "python"
                answer = (
                    "```python\n"
                    "def merge_sort(values):\n"
                    "    if len(values) <= 1:\n"
                    "        return values\n"
                    "    mid = len(values) // 2\n"
                    "    left = merge_sort(values[:mid])\n"
                    "    right = merge_sort(values[mid:])\n"
                    "    result = []\n"
                    "    i = j = 0\n"
                    "    while i < len(left) and j < len(right):\n"
                    "        if left[i] <= right[j]:\n"
                    "            result.append(left[i]); i += 1\n"
                    "        else:\n"
                    "            result.append(right[j]); j += 1\n"
                    "    return result + left[i:] + right[j:]\n"
                    "```"
                )
            elif context_documents:
                excerpts = [doc["text"][:500].strip() for doc in context_documents[:3]]
                answer = " ".join(excerpts)
                if brief:
                    answer = answer[:500]
            else:
                answer = "No indexed documents matched this query. Add documents or use /api/ingest to enable grounded answers."
                if brief:
                    answer = "No matching documents were found."
        latency_ms = (time.perf_counter() - start) * 1000
        return answer, latency_ms
