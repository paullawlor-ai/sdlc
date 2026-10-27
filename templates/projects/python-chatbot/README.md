# Python Chatbot Template

A terminal chatbot starter with conversation memory, a direct HTTPX LLM client,
structured logging, and extension points for retrieval and application safety.

## Quick Start

Initialize the starter from the host project root:

```bash
python sdlc/scripts/init_project.py python-chatbot
python -m pip install -r requirements.txt
```

Create a local `.env` containing `LLM_API_KEY` and the `LLM_MODEL` you intend to
use, or set those environment variables in your shell. Supply your own values;
do not commit the API key. Run:

```bash
python -m app.main
```

Live chat requests call the LLM provider and require network access. The smoke
test initializes the engine without making a request.

## Project Structure

```text
app/
  __init__.py
  main.py
  config.py
  chat/
    __init__.py
    engine.py
    memory.py
    prompts.py
  rag/
    __init__.py
    retriever.py
  safety/
    __init__.py
    input.py
    output.py
  utils/
    __init__.py
    logging.py
tests/
  __init__.py
  test_smoke.py
requirements.txt
requirements-dev.txt
ruff.toml
README.md
```

## Implemented Behavior and Extension Points

The engine retains a bounded conversation history, builds messages, and calls
the provider through HTTPX. Input handling normalizes whitespace, limits length,
and screens a small list of patterns. Logging records interaction metadata.

The RAG retriever returns empty context and does not index documents. Keep
`RAG_ENABLED=false` until you implement and review retrieval and embeddings;
vector-store and embedding packages are not installed. The output validator is
an extension point that currently returns the response unchanged. Rate limiting
is not implemented. Pattern screening is a demonstration, not a prompt-injection
security boundary or a complete implementation of the S0/A0 baselines.

## Configuration

Settings in `app/config.py` read environment variables and a local `.env`:

| Variable | Purpose | Default |
| --- | --- | --- |
| `LLM_API_KEY` | Credential for live requests | Empty |
| `LLM_MODEL` | Model for live requests | `gpt-4` |
| `LLM_MAX_TOKENS` | Response token limit | `1000` |
| `MAX_CONVERSATION_TURNS` | Retained conversation turns | `10` |
| `RAG_ENABLED` | Instantiate the retrieval placeholder | `false` |
| `RAG_DOCUMENTS_PATH` | Path reserved for retrieval implementation | `./data/docs` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Quality Checks and Next Steps

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check app tests
python -m ruff format --check app tests
python -m pytest -q
```

Add requirements to `sdlc_artifacts/requirements/` and start with
`Read sdlc/prompts/bootstrap.md and begin`. Select production controls using the
application's threat model. From the host root, run
`python sdlc/scripts/security_scan.py` and link its report in required reviews;
see `sdlc/docs/framework/quality-and-security.md` for scope and freshness.
