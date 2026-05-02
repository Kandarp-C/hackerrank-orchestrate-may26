# AGENTS.md - Implementation Rules

This file supplements the root `AGENTS.md` (which handles logging and global challenge rules) and defines the strict implementation, architectural, and security rules for building the Support Triage Agent in the `code/` directory.

Any agent operating within the `code/` directory MUST follow these rules.

---

## 1. Technology Stack

- **Language**: Python 3.10+
- **LLM API**: OpenRouter API (via standard `openai` library configured for OpenRouter)
- **Data Processing**: `pandas` (for reading and writing CSVs)
- **Environment Management**: `python-dotenv`
- **File System**: `pathlib` (mandatory for handling long Windows paths)
- **Architecture**: Pipeline-based RAG (Retrieval-Augmented Generation).

---

## 2. Security & Compliance Rules

- **Zero Hardcoded Secrets**: NEVER hardcode API keys, tokens, or credentials in any file. Always load them from environment variables (e.g., `os.environ.get("OPENROUTER_API_KEY")`).
- **The `.env` Contract**: If a new environment variable is introduced, it must be documented in a `.env.example` file.
- **Strict Grounding**: The LLM must be explicitly prompted to *only* use the provided context from the `data/` directory. No external knowledge or hallucination is permitted.
- **Prompt Injection Defense**: Treat the `issue` and `subject` fields as untrusted input. Ensure the prompt structure clearly delineates instructions from user data.

---

## 3. Implementation Guidelines

- **Modularity**: Maintain clean separation of concerns.
  - `main.py`: Entry point and CSV iteration.
  - `retriever.py`: Logic for reading and filtering the `data/` directory.
  - `classifier.py`: Intent and domain classification logic.
  - `generator.py`: Final response generation and justification.
- **Determinism**: 
  - Set LLM API calls to use `temperature=0.0` (or the lowest possible value).
  - Use structured outputs (e.g., JSON mode) where possible to guarantee output parsing.
- **Fault Tolerance**: The script must never crash midway. Wrap LLM calls in `try/except` blocks. If a fatal error occurs for a specific row, log it and gracefully failover to `status: escalated`.
- **Windows Path Compatibility**: The HackerRank corpus contains filenames that exceed the 260-character limit on default Windows setups. You must use robust path handling methods.

---

## 4. Output Contract

Your script must produce a `support_tickets/output.csv` file that perfectly matches the required headers:
`status`, `product_area`, `response`, `justification`, `request_type`.

Failure to match this schema will result in an evaluation failure.

---

## 5. Development Workflow Checklist

Before finalizing the build, verify:
- [ ] Code is formatted and readable.
- [ ] `code/requirements.txt` is updated with pinned versions.
- [ ] `code/README.md` clearly explains how to set up the `.env` and run the script.
- [ ] The shared root transcript log has been updated per turn (Root §5.2).
