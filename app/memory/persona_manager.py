from typing import List


class PersonaManager:
    def build_persona(self, memories: List[dict]) -> str:
        language = "a practical language"
        style = "clear and concise"
        for memory in memories:
            fact = memory["fact"].lower()
            if memory["category"] == "preferred_language" and "preferred language:" in fact:
                language = fact.split(":", 1)[1].strip()
            if "brief" in fact:
                style = "brief"
            if "code-only" in fact:
                style = "code-only"
        return f"Use {language}. Respond in a {style} style."
