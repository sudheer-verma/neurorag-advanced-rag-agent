from app.memory.fact_extractor import extract_facts
from app.memory.memory_manager import MemoryManager
from app.memory.persona_manager import PersonaManager


def test_fact_extraction(tmp_path):
    facts = extract_facts("Hello! I work in Python and prefer brief, code-only responses.")
    categories = {item["category"] for item in facts}
    assert "preferred_language" in categories
    assert "response_style" in categories
    assert "output_style" in categories


def test_memory_persistence_and_user_isolation(tmp_path):
    manager = MemoryManager(str(tmp_path / "memory.sqlite"))
    manager.add("usr_1", "Preferred language: Python", "preferred_language", "session_1")
    manager.add("usr_2", "Response preference: detailed", "response_style", "session_2")
    assert len(manager.get("usr_1")) == 1
    assert len(manager.get("usr_2")) == 1
    persona = PersonaManager().build_persona(manager.get("usr_1"))
    assert "python" in persona
