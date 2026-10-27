# Python FastAPI AI Service Template

A FastAPI starter with a JSON completion endpoint, direct HTTPX LLM requests,
Pydantic validation, structured logging, request IDs, rate limiting, health
endpoints, and a Dockerfile. Authentication and authorization are not implemented.

## Quick Start

From the host project root:

```bash
python sdlc/scripts/init_project.py python-fastapi-ai
python -m pip install -r requirements.txt
```

Create a local `.env` containing `LLM_API_KEY` and the `LLM_MODEL` you intend to
use, or set those environment variables in your shell. Supply your own values;
do not commit the API key. Start the service:

```bash
uvicorn app.main:app --reload
```

`GET /health` and `GET /ready` return status dictionaries. The readiness endpoint
is a placeholder and does not verify external dependencies.
`POST /api/v1/complete` accepts JSON with `prompt` and optional `max_tokens`.
Live completions require provider credentials and network access.

## Project Structure

```text
app/
  __init__.py
  main.py
  config.py
  api/
    __init__.py
    routes.py
    dependencies.py
  core/
    __init__.py
    logging.py
    rate_limit.py
  llm/
    __init__.py
    client.py
    safety.py
tests/
  __init__.py
  conftest.py
  test_api.py
  test_safety.py
requirements.txt
requirements-dev.txt
ruff.toml
Dockerfile
README.md
```

## Configuration

Settings in `app/config.py` read environment variables and a local `.env`:

| Variable | Purpose | Default |
| --- | --- | --- |
| `LLM_API_KEY` | Credential for live requests | Empty |
| `LLM_MODEL` | Model for live requests | `gpt-4` |
| `LLM_MAX_TOKENS` | Default limit for direct client calls | `1000` |
| `RATE_LIMIT_REQUESTS` | Limiter default request allowance | `60` |
| `RATE_LIMIT_PERIOD` | Limiter default interval in seconds | `60` |
| `LOG_LEVEL` | Logging level | `INFO` |

The completion route has its own `10/minute` limit. Its request schema defaults
`max_tokens` to `500` and accepts values from `1` through `4000`.

## LLM Integration

Call the async client with its actual keyword parameters:

```python
from app.llm.client import get_completion
from app.llm.safety import sanitize_input, validate_output

async def complete_text(user_text: str) -> str:
    result = await get_completion(
        prompt=sanitize_input(user_text),
        max_tokens=500,
    )
    return validate_output(result["content"])
```

Input screening redacts a few obvious patterns; output inspection logs matching
code markers but returns the text unchanged. These demonstrations are not a
prompt-injection boundary or a complete implementation of S0/A0. Select access
controls, output enforcement, data boundaries, and operational controls for the
application's threat model before production use.

## Testing and Quality Checks

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check app tests
python -m ruff format --check app tests
python -m pytest -q
python -m pytest --cov=app
```

## Deployment and Next Steps

With a locally configured `.env`:

```bash
docker build -t my-ai-service .
docker run -p 8000:8000 --env-file .env my-ai-service
```

Add requirements to `sdlc_artifacts/requirements/` and start with
`Read sdlc/prompts/bootstrap.md and begin`. From the host root, run
`python sdlc/scripts/security_scan.py` and link its report in required reviews;
see `sdlc/docs/framework/quality-and-security.md` for scope and freshness.
