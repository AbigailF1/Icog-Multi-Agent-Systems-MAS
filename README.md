# Incident Response War Room (CrewAI)

## Overview

This repository implements a Multi‑Agent System (MAS) using CrewAI. It simulates an incident response “war room” where specialized agents collaborate to triage an outage, synthesize findings, and draft stakeholder communications. The system is designed to demonstrate MAS concepts (autonomy, coordination, delegation, and shared context) in a structured workflow.

## What This Repo Contains

- **CrewAI agents** with distinct roles, goals, and tools.
- **Task pipeline** that routes work across agents and merges findings.
- **Crew orchestration** with configurable “safe” and “survival” modes for free‑tier LLM limits.
- **Streamlit UI** for interactive demos.

## How It Works

### 1) Agents

Defined in [src/crew/agents.py](src/crew/agents.py). Each agent has:

- A role (e.g., Incident Commander, SRE Triage, Comms Lead)
- A goal and backstory
- A toolset for environment interaction

### 2) Tools (Simulation Layer)

Defined in [src/crew/tools.py](src/crew/tools.py). These are stub tools that simulate metrics, logs, config diffs, and status updates. In a real system, these would call actual services (e.g., Datadog, Splunk, Jira, Statuspage).

### 3) Tasks

Defined in [src/crew/tasks.py](src/crew/tasks.py). The tasks drive the workflow:

- Triage → App/DB/Security checks → Commander synthesis → Comms report

### 4) Crew Orchestration

Defined in [src/crew/crew.py](src/crew/crew.py). The crew coordinates agents and tasks. The behavior is controlled by environment flags:

- **SAFE_MODE**: Sequential execution to reduce LLM calls.
- **SURVIVAL_MODE**: Reduced 3‑agent workflow (Commander, SRE, Comms).
- **MEMORY_ENABLED**: Enable/disable memory embeddings.

### 5) UI

Defined in [src/ui.py](src/ui.py). A Streamlit interface for running incidents and viewing outputs.

## Running the Project

### 1) Install dependencies

Use your existing venv, then install:

- crewai
- crewai[google-genai]
- google-generativeai
- streamlit

### 2) Configure Environment

Copy [.env.example](.env.example) to `.env` and fill in your key.

### 3) Run the UI

```
python -m streamlit run src/ui.py
```

### 4) CLI Demo

```
python src/run_demo.py "Payments API returns 500s after a deploy; customer complaints increasing."
```

## Notes on Outputs

The system **simulates** realistic incident details (version numbers, config keys, timeline) based on the prompt. It is intended to demonstrate MAS coordination rather than to reflect real telemetry.

## Files Map

- [src/crew/agents.py](src/crew/agents.py) — Agents and LLM selection
- [src/crew/tools.py](src/crew/tools.py) — Tool stubs
- [src/crew/tasks.py](src/crew/tasks.py) — Task definitions
- [src/crew/crew.py](src/crew/crew.py) — Orchestration
- [src/run_demo.py](src/run_demo.py) — CLI demo
- [src/ui.py](src/ui.py) — Streamlit UI

## Suggested Demo Scenarios

1. **Standard**: “Checkout service down; new DB migration pushed.”
2. **Red Herring**: “Slow loading; frontend suspects DDoS, backend suspects DB.”
3. **Ambiguous**: “CPU spikes across clusters; no deploys; no obvious logs.”
