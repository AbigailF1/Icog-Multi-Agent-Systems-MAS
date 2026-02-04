from crewai import Task


def build_tasks(agents: dict, incident_input: str) -> dict[str, Task]:
    triage = Task(
        description=(
            "Triage the incident using available signals. Identify likely root cause "
            "and immediate stabilizing actions.\n\n"
            f"Incident: {incident_input}"
        ),
        agent=agents["sre_triage"],
        expected_output="Root cause hypothesis + immediate mitigation steps.",
    )

    app_check = Task(
        description=(
            "Inspect recent deploys/config changes and identify risky diffs or rollbacks.\n\n"
            f"Incident: {incident_input}"
        ),
        agent=agents["app_engineer"],
        expected_output="Suspicious deploy/config changes and rollback options.",
    )

    db_check = Task(
        description=(
            "Analyze DB performance signals and query hotspots; propose fixes.\n\n"
            f"Incident: {incident_input}"
        ),
        agent=agents["database_specialist"],
        expected_output="DB bottlenecks + concrete remediation steps.",
    )

    security_check = Task(
        description=(
            "Assess security alerts or indicators of compromise; propose containment.\n\n"
            f"Incident: {incident_input}"
        ),
        agent=agents["security_analyst"],
        expected_output="Security risk assessment + containment actions.",
    )

    commander = Task(
        description=(
            "Combine findings, set severity, decide on action plan, and assign owners.\n\n"
            f"Incident: {incident_input}"
        ),
        agent=agents["incident_commander"],
        expected_output="Severity level, action plan, and owner assignments.",
        context=[triage, app_check, db_check, security_check],
    )

    comms = Task(
        description=(
            "Draft stakeholder update and post-incident summary outline.\n\n"
            f"Incident: {incident_input}"
        ),
        agent=agents["comms_lead"],
        expected_output="Status update + post-incident summary outline.",
        context=[commander],
    )

    return {
        "triage": triage,
        "app_check": app_check,
        "db_check": db_check,
        "security_check": security_check,
        "commander": commander,
        "comms": comms,
    }
