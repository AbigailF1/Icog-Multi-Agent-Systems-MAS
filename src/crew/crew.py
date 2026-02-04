import os
from pathlib import Path

from crewai import Crew, Process
from crewai.memory.short_term.short_term_memory import ShortTermMemory

from .agents import build_agents, build_llm
from .tasks import build_tasks


def build_embedder_config() -> dict | None:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    return {
        "provider": "google-generativeai",
        "config": {
            "api_key": api_key,
            "model_name": "gemini-embedding-001",
        },
    }


def build_memory_path() -> str:
    model = os.getenv("LLM_MODEL", "default")
    safe = model.replace("/", "_").replace(":", "_")
    root = Path(__file__).resolve().parents[2]
    return str(root / ".crewai_memory" / safe)


def memory_enabled() -> bool:
    value = os.getenv("MEMORY_ENABLED", "true").strip().lower()
    return value in {"1", "true", "yes", "y"}


def safe_mode_enabled() -> bool:
    value = os.getenv("SAFE_MODE", "false").strip().lower()
    return value in {"1", "true", "yes", "y"}


def survival_mode_enabled() -> bool:
    value = os.getenv("SURVIVAL_MODE", "false").strip().lower()
    return value in {"1", "true", "yes", "y"}


def build_crew(incident_input: str, tools: dict | None = None) -> Crew:
    agents = build_agents(tools)
    tasks = build_tasks(agents, incident_input)
    survival_mode = survival_mode_enabled()
    safe_mode = safe_mode_enabled()
    use_memory = memory_enabled() and not safe_mode and not survival_mode
    embedder = build_embedder_config() if use_memory else None
    short_term_memory = None
    if use_memory and embedder:
        memory_path = build_memory_path()
        short_term_memory = ShortTermMemory(embedder_config=embedder, path=memory_path)

    crew_agents = list(agents.values())
    crew_tasks = list(tasks.values())
    process = Process.sequential if (safe_mode or survival_mode) else Process.hierarchical
    manager_llm = None if (safe_mode or survival_mode) else build_llm()

    if survival_mode:
        crew_agents = [
            agents["incident_commander"],
            agents["sre_triage"],
            agents["comms_lead"],
        ]
        crew_tasks = [
            tasks["triage"],
            tasks["commander"],
            tasks["comms"],
        ]

    return Crew(
        agents=crew_agents,
        tasks=crew_tasks,
        process=process,
        manager_llm=manager_llm,
        memory=use_memory,
        embedder=embedder,
        short_term_memory=short_term_memory,
        verbose=True,
    )
