import io
import os
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src2"))

import streamlit as st

from pdf_summarizer import build_pdf_crew, load_env, read_pdf_text


def main() -> None:
    load_env()

    st.set_page_config(page_title="PDF Summarizer MAS", layout="wide")
    st.title("PDF Summarizer (Mini MAS)")
    st.caption("Two-agent workflow: Extractor → Summarizer")

    input_mode = st.radio("Input type", ["PDF", "Text"], horizontal=True)

    uploaded = None
    text_input = ""

    if input_mode == "PDF":
        uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    else:
        text_input = st.text_area(
            "Paste text",
            height=220,
            placeholder="Paste or type text to summarize...",
        )

    if input_mode == "PDF" and uploaded is None:
        st.info("Upload a PDF to begin.")
        return

    if input_mode == "Text" and not text_input.strip():
        st.info("Enter some text to begin.")
        return

    run = st.button("Summarize", type="primary")

    if run:
        output = io.StringIO()
        status = st.empty()
        progress = st.progress(0)

        if input_mode == "PDF":
            status.info("Reading PDF...")
            progress.progress(10)
            with st.spinner("Reading PDF..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = Path(tmp.name)

                try:
                    doc_text = read_pdf_text(tmp_path)
                finally:
                    os.unlink(tmp_path)
        else:
            status.info("Preparing text...")
            progress.progress(10)
            doc_text = text_input.strip()

        max_chars = int(os.getenv("PDF_MAX_CHARS", "12000"))
        if len(doc_text) > max_chars:
            st.warning(
                f"PDF text is long ({len(doc_text):,} chars). "
                f"Truncating to {max_chars:,} chars to avoid long LLM calls."
            )
            doc_text = doc_text[:max_chars]

        has_google = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
        has_openai = bool(os.getenv("OPENAI_API_KEY"))
        if not (has_google or has_openai):
            st.error(
                "No LLM configured. Set GOOGLE_API_KEY or GEMINI_API_KEY, or OPENAI_API_KEY in .env."
            )
            return

        status.info("Running crew...")
        progress.progress(50)
        with st.spinner("Running crew..."):
            try:
                crew = build_pdf_crew(doc_text)
                with redirect_stdout(output):
                    result = crew.kickoff()
            except Exception as exc:
                status.error("Failed")
                st.error(f"Summarization failed: {exc}")
                return
        progress.progress(100)
        status.success("Complete")
        st.success("Complete")
        st.subheader("Summary")

        def extract_summary(value) -> str:
            if value is None:
                return ""
            if isinstance(value, str):
                return value.strip()
            if isinstance(value, dict):
                if isinstance(value.get("raw"), str):
                    return value["raw"].strip()
                tasks = value.get("tasks_output") or []
                if tasks:
                    last = tasks[-1]
                    if isinstance(last, dict) and isinstance(last.get("raw"), str):
                        return last["raw"].strip()
            raw = getattr(value, "raw", None)
            if isinstance(raw, str):
                return raw.strip()
            tasks = getattr(value, "tasks_output", None)
            if tasks:
                last = tasks[-1]
                last_raw = getattr(last, "raw", None)
                if isinstance(last_raw, str):
                    return last_raw.strip()
            return str(value).strip()

        summary_text = extract_summary(result)
        st.write(summary_text if summary_text else "(No summary text returned)")

        with st.expander("Raw output"):
            st.write(result)

        with st.expander("Agent Internal Reasoning (verbose logs)"):
            st.text(output.getvalue())


if __name__ == "__main__":
    main()
