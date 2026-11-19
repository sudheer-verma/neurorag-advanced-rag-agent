import re
from typing import List


def extract_facts(message: str) -> List[dict]:
    facts = []
    language_match = re.search(r"\b(?:work in|use|prefer|language is)\s+([A-Za-z][A-Za-z0-9+#.]*)", message, re.I)
    if language_match:
        language = language_match.group(1).strip()
        facts.append({"category": "preferred_language", "fact": f"Preferred language: {language}"})

    if re.search(r"\bbrief\b", message, re.I):
        facts.append({"category": "response_style", "fact": "Response preference: brief"})
    if re.search(r"\b(?:code-only|code only)\b", message, re.I):
        facts.append({"category": "output_style", "fact": "Output preference: code-only"})
    if re.search(r"\bdetailed\b", message, re.I):
        facts.append({"category": "response_style", "fact": "Response preference: detailed"})
    return facts
