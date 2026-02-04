import os
import sys
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
    
    # Allow taking the incident from command line arguments
    incident_input = " ".join(sys.argv[1:]).strip() or DEFAULT_INCIDENT
    
    print("\n" + "="*50)
    print(f"🚀 INITIALIZING MULTI-AGENT RESEARCH LAB")
    print(f"STIMULATING INCIDENT: {incident_input}")
    print("="*50 + "\n")

    # Build the Crew (Memory and Hierarchical process are already inside build_crew)
    crew = build_crew(incident_input)
    
    # Kickoff the process
    # The 'verbose=True' in your crew.py will show the "Thoughts" automatically
    result = crew.kickoff()

    print("\n" + "="*50)
    print("🏁 INCIDENT RESOLUTION COMPLETE")
    print("="*50)
    
    # Print the final synthesized output from the Comms Lead/Commander
    print(f"\nFINAL MISSION REPORT:\n{result}")
    
    # Optional: Print usage metrics to show the 'efficiency' of the MAS
    if hasattr(result, 'token_usage'):
        print("\n" + "-"*30)
        print(f"Efficiency Metrics: {result.token_usage}")
        print("-"*30)

if __name__ == "__main__":
    main()