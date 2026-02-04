import io
import os
from contextlib import redirect_stdout

import streamlit as st

from crew.crew import build_crew


DEFAULT_INCIDENT = "Payments API returns 500s after a deploy; customer complaints increasing."


def load_env() -> None:
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"")
            os.environ[key] = value


def main() -> None:
    load_env()

    st.set_page_config(page_title="Incident Response MAS", layout="wide")
    st.title("Incident Response War Room")
    st.caption("Multi‑Agent System powered by CrewAI")

    with st.sidebar:
        st.subheader("Agent Team")
        st.markdown(
            """
- Incident Commander
- SRE Triage
- App Engineer
- Database Specialist
- Security Analyst
- Comms Lead
"""
        )
        st.divider()
        st.markdown("Use a realistic incident to see coordination and synthesis.")

    incident = st.text_area("Describe the incident", value=DEFAULT_INCIDENT, height=120)
    run = st.button("Assemble Crew", type="primary")

    if run:
        output = io.StringIO()
        with st.spinner("Running crew..."):
            crew = build_crew(incident)
            with redirect_stdout(output):
                result = crew.kickoff()

        st.success("Complete")

        st.subheader("Final Mission Report")
        st.write(result)

        with st.expander("Agent Internal Reasoning (verbose logs)"):
            st.text(output.getvalue())


if __name__ == "__main__":
    main()
