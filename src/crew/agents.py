import os

from crewai import Agent, LLM

from .tools import build_tools


def build_llm() -> LLM | None:
    model = os.getenv("LLM_MODEL")
    if model:
        if "gemini" in model and not (
            os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        ):
            return None
        if "gpt" in model and not os.getenv("OPENAI_API_KEY"):
            return None
        try:
            return LLM(model=model)
        except ImportError:
            return None

    if os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
        return LLM(model="gemini/gemini-1.5-flash")

    if os.getenv("OPENAI_API_KEY"):
        return LLM(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    return None


def build_agents(tools: dict | None = None) -> dict[str, Agent]:
    tools = tools or build_tools()
    llm = build_llm()
    max_rpm_env = os.getenv("AGENT_MAX_RPM")
    max_rpm = int(max_rpm_env) if max_rpm_env else None

    def pick(*names: str):
        return [tool for tool in (tools.get(name) for name in names) if tool]

    incident_commander = Agent(
        role="Incident Commander",
        goal="Coordinate response, set severity, and make final decisions.",
        backstory=(
            "Veteran incident lead with cross-team authority and a focus on "
            "rapid stabilization."
        ),
        llm=llm,
        tools=pick("incident_tracker", "status_page"),
        allow_delegation=True,
        max_rpm=max_rpm,
    )

    sre_triage = Agent(
        role="SRE Triage",
        goal="Analyze metrics/logs and isolate the likely root cause.",
        backstory="On-call SRE specializing in observability and rapid diagnosis.",
        llm=llm,
        tools=pick("metrics", "logs"),
        allow_delegation=False,
        max_rpm=max_rpm,
    )

    app_engineer = Agent(
        role="App Engineer",
        goal="Inspect recent deploys/config changes and application behavior.",
        backstory="Senior backend engineer familiar with the release pipeline.",
        llm=llm,
        tools=pick("deploy_history", "config_repo"),
        allow_delegation=False,
        max_rpm=max_rpm,
    )

    database_specialist = Agent(
        role="Database Specialist",
        goal="Diagnose database performance, query issues, and scaling risks.",
        backstory="DBA experienced with performance tuning and indexing.",
        llm=llm,
        tools=pick("db_metrics", "query_analyzer"),
        allow_delegation=False,
        max_rpm=max_rpm,
    )

    security_analyst = Agent(
        role="Security Analyst",
        goal="Assess alerts, containment actions, and security risk.",
        backstory="SOC analyst focused on rapid threat assessment and triage.",
        llm=llm,
        tools=pick("siem", "threat_intel"),
        allow_delegation=False,
        max_rpm=max_rpm,
    )

    comms_lead = Agent(
        role="Comms Lead",
        goal="Draft stakeholder updates and post-incident summary.",
        backstory="Technical communicator for incident updates and reporting.",
        llm=llm,
        tools=pick("status_page", "incident_tracker"),
        allow_delegation=False,
        max_rpm=max_rpm,
    )

    return {
        "incident_commander": incident_commander,
        "sre_triage": sre_triage,
        "app_engineer": app_engineer,
        "database_specialist": database_specialist,
        "security_analyst": security_analyst,
        "comms_lead": comms_lead,
    }
