# Support Triage Agent

A terminal-based AI agent that triages support tickets across HackerRank, Claude, and Visa using a modular RAG (Retrieval-Augmented Generation) pipeline.

## Architecture

1.  **Corpus Loader**: Recursively scans the `data/` directory, parsing Markdown files and extracting titles/content.
2.  **Retriever**: A two-tier filtering system. It first isolates the relevant company domain, then uses keyword-based scoring to find the most relevant articles. Small domains (Visa) and index files are automatically "stuffed" into context for maximum grounding.
3.  **Agent (Classifier & Generator)**: Uses the OpenRouter API with a strict system prompt to classify the ticket into product areas and request types. It decides whether to `reply` or `escalate` based on safety and context availability.
4.  **Orchestrator**: Manages the CSV workflow, ensuring deterministic results (`temperature=0.0`) and graceful error handling.

## Setup

1.  **Environment**: Python 3.10+
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configuration**:
    - Copy `.env.example` to `.env`.
    - Add your `OPENROUTER_API_KEY`.
    - (Optional) Change `OPENROUTER_MODEL` (default is `google/gemini-2.0-flash-001`).

## Usage

Run the agent from the `code/` directory:

```bash
python main.py
```

The agent will:
- Load the local corpus.
- Process `../support_tickets/support_tickets.csv`.
- Write results to `../support_tickets/output.csv`.

## Design Decisions

- **Strict Grounding**: The agent is explicitly forbidden from using external knowledge. If an answer isn't in the context, it escalates.
- **Fail-Safe Escalation**: Any processing error or ambiguous high-risk situation (billing, fraud, identity) triggers an automatic escalation to a human.
- **Path Handling**: Uses `pathlib` to ensure compatibility with Windows long file paths.
- **Deterministic Output**: LLM calls use temperature 0.0 to ensure consistent evaluation scores.
