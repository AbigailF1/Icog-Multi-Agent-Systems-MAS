import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from crewai import Agent, Crew, Process, Task

from crew.agents import build_llm


def load_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"')


def read_pdf_text(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise SystemExit("Install pypdf: pip install pypdf") from exc

    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages).strip()
    if not text:
        raise SystemExit("No extractable text found in the PDF.")
    return text


def build_pdf_crew(doc_text: str) -> Crew:
    llm = build_llm()
    if llm is None:
        raise RuntimeError(
            "No LLM configured. Set GOOGLE_API_KEY or OPENAI_API_KEY (or LLM_MODEL)."
        )

    extractor = Agent(
        role="Document Extractor",
        goal="Pull key points and facts from the provided document.",
        backstory="Focused on accurate extraction without adding new facts.",
        llm=llm,
    )

    summarizer = Agent(
        role="Summarizer",
        goal="Write a concise summary based on extracted points only.",
        backstory="Produces clear, short summaries for quick review.",
        llm=llm,
    )

    extract_task = Task(
        description=(
            "Extract the top 8-12 key points from this document.\n\n"
            f"Document:\n{doc_text}"
        ),
        agent=extractor,
        expected_output="Bullet list of key points.",
    )

    summarize_task = Task(
        description=(
            "Write a short summary (6-10 sentences) using only the extracted points."
        ),
        agent=summarizer,
        expected_output="Concise summary paragraph(s).",
        context=[extract_task],
    )

    return Crew(
        agents=[extractor, summarizer],
        tasks=[extract_task, summarize_task],
        process=Process.sequential,
        memory=False,
        verbose=True,
    )


def main() -> None:
    load_env()
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python src2/pdf_summarizer.py <path-to-pdf>")

    pdf_path = Path(sys.argv[1]).resolve()
    if not pdf_path.exists():
        raise SystemExit(f"File not found: {pdf_path}")

    doc_text = read_pdf_text(pdf_path)
    crew = build_pdf_crew(doc_text)
    result = crew.kickoff()
    print(result)


if __name__ == "__main__":
    main()
