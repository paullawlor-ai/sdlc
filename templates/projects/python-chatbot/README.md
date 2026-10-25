# Python Chatbot Template

A template for building conversational AI chatbots with RAG (Retrieval Augmented Generation) support.

## Features

- Conversational AI with memory
- RAG integration for knowledge base
- Security baselines (S0 + A0) built-in
- Prompt injection protection
- Structured logging
- Rate limiting
- Conversation history management

## Quick Start

1. Initialize from this template:
   ```bash
   python sdlc/scripts/init_project.py python-chatbot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

4. Run the chatbot:
   ```bash
   python -m app.main
   ```

## Project Structure

```
+-- app/
|   +-- __init__.py
|   +-- main.py              # Chatbot entry point
|   +-- config.py            # Configuration
|   +-- chat/
|   |   +-- __init__.py
|   |   +-- engine.py        # Chat engine
|   |   +-- memory.py        # Conversation memory
|   |   +-- prompts.py       # System prompts
|   +-- rag/
|   |   +-- __init__.py
|   |   +-- retriever.py     # Document retrieval
|   |   +-- chunker.py       # Document chunking
|   +-- safety/
|   |   +-- __init__.py
|   |   +-- input.py         # Input sanitization
|   |   +-- output.py        # Output validation
|   +-- utils/
|       +-- __init__.py
|       +-- logging.py       # Structured logging
+-- tests/
+-- requirements.txt
+-- README.md
```

## Security Baselines

This template implements:

### S0 - Base Security
- Input validation
- Structured logging (no secrets)
- Rate limiting

### A0 - AI Security
- Prompt injection detection
- Context boundary enforcement
- Output validation
- Token limits
- Audit logging

## Key Concepts

### Conversation Memory
```python
from app.chat.memory import ConversationMemory

memory = ConversationMemory(max_turns=10)
memory.add_user_message("Hello!")
memory.add_assistant_message("Hi there!")
```

### RAG Integration
```python
from app.rag.retriever import Retriever

retriever = Retriever(documents_path="./data/docs")
context = retriever.get_relevant_context(query)
```

### Safety Controls
```python
from app.safety.input import sanitize_user_input
from app.safety.output import validate_response

safe_input = sanitize_user_input(user_message)
validated = validate_response(llm_response)
```

## Configuration

Key settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_API_KEY` | API key for LLM | (required) |
| `LLM_MODEL` | Model to use | gpt-4 |
| `MAX_CONVERSATION_TURNS` | History length | 10 |
| `RAG_ENABLED` | Enable RAG | false |
| `RAG_DOCUMENTS_PATH` | Knowledge base path | ./data/docs |

## Next Steps

1. Add your requirements to `sdlc_artifacts/requirements/`
2. Run the bootstrap prompt in Cursor
3. Follow the SDLC phases to build your chatbot


## Quality checks

The RAG retriever is a placeholder. Select and security-review a retrieval store
and embedding implementation before enabling it; optional vector-store/model
packages are not installed by this starter.

Install development tools separately, then run these commands from this project:

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check app tests
python -m ruff format --check app tests
python -m pytest -q
```

When using the SDLC framework, run `python sdlc/scripts/security_scan.py` from the
host project root and link its report in the security review. It runs Bandit,
detect-secrets, and pip-audit. Scan failures and unresolved findings block required
reviews. See `sdlc/docs/framework/quality-and-security.md` for scope and freshness.
