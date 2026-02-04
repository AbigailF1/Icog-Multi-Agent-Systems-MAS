from crewai.tools import BaseTool


class MetricsTool(BaseTool):
    name: str = "metrics"
    description: str = "Check service metrics and error rates for the incident."

    def _run(self, query: str) -> str:
        return f"Metrics snapshot for incident context: {query}"


class LogsTool(BaseTool):
    name: str = "logs"
    description: str = "Fetch recent logs and error traces related to the incident."

    def _run(self, query: str) -> str:
        return f"Recent log highlights for incident context: {query}"


class DeployHistoryTool(BaseTool):
    name: str = "deploy_history"
    description: str = "Inspect recent deploys and rollbacks for the service."

    def _run(self, service: str) -> str:
        return f"Recent deploy history for {service}: last deploy at T-30m"


class ConfigRepoTool(BaseTool):
    name: str = "config_repo"
    description: str = "Check recent config changes that could affect stability."

    def _run(self, service: str) -> str:
        return f"Config diffs for {service}: no critical changes detected"


class DBMetricsTool(BaseTool):
    name: str = "db_metrics"
    description: str = "Check database CPU, connections, and slow query rates."

    def _run(self, db: str) -> str:
        return f"DB metrics for {db}: CPU stable, connections within limits"


class QueryAnalyzerTool(BaseTool):
    name: str = "query_analyzer"
    description: str = "Analyze slow queries and execution plans."

    def _run(self, db: str) -> str:
        return f"Top slow queries for {db}: none above threshold"


class SIEMTool(BaseTool):
    name: str = "siem"
    description: str = "Review security alerts and indicators of compromise."

    def _run(self, query: str) -> str:
        return f"SIEM summary for incident context: {query}"


class ThreatIntelTool(BaseTool):
    name: str = "threat_intel"
    description: str = "Check recent threat intelligence relevant to the incident."

    def _run(self, query: str) -> str:
        return f"Threat intel check complete for: {query}"


class IncidentTrackerTool(BaseTool):
    name: str = "incident_tracker"
    description: str = "Update incident tracker with status and actions."

    def _run(self, update: str) -> str:
        return f"Incident tracker updated: {update}"


class StatusPageTool(BaseTool):
    name: str = "status_page"
    description: str = "Post a status update for stakeholders."

    def _run(self, update: str) -> str:
        return f"Status page update drafted: {update}"


def build_tools() -> dict[str, BaseTool]:
    return {
        "metrics": MetricsTool(),
        "logs": LogsTool(),
        "deploy_history": DeployHistoryTool(),
        "config_repo": ConfigRepoTool(),
        "db_metrics": DBMetricsTool(),
        "query_analyzer": QueryAnalyzerTool(),
        "siem": SIEMTool(),
        "threat_intel": ThreatIntelTool(),
        "incident_tracker": IncidentTrackerTool(),
        "status_page": StatusPageTool(),
    }
