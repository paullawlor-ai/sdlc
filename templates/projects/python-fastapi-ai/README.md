# Python FastAPI AI Service Template

A template for building AI-infused FastAPI services with security best practices.

## Features

- FastAPI with async support
- LLM integration patterns
- Security baselines (S0 + A0) built-in
- Structured logging with correlation IDs
- Input validation with Pydantic
- Rate limiting
- Health check endpoints
- Docker support

## Quick Start

1. Initialize from this template:
   ```bash
   python sdlc/scripts/init_project.py python-fastapi-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Run the service:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

```
+-- app/
|   +-- __init__.py
|   +-- main.py              # FastAPI app entry
|   +-- config.py            # Configuration
|   +-- api/
|   |   +-- __init__.py
|   |   +-- routes.py        # API routes
|   |   +-- dependencies.py  # Auth, validation deps
|   +-- core/
|   |   +-- __init__.py
|   |   +-- security.py      # Auth/authz
|   |   +-- logging.py       # Structured logging
|   +-- llm/
|   |   +-- __init__.py
|   |   +-- client.py        # LLM client wrapper
|   |   +-- prompts.py       # Prompt templates
|   |   +-- safety.py        # Input/output safety
|   +-- models/
|       +-- __init__.py
|       +-- schemas.py       # Pydantic models
+-- tests/
|   +-- __init__.py
|   +-- conftest.py
|   +-- test_api.py
+-- requirements.txt
+-- Dockerfile
+-- .env.example
+-- README.md
```

## Security Baselines

This template implements:

### S0 - Base Security
- Input validation via Pydantic
- Structured logging (no secrets)
- CORS configuration
- Rate limiting
- Health checks

### A0 - AI Security
- Input sanitization before LLM
- Output validation
- Token limits
- Tool parameter validation
- AI action audit logging

## Configuration

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_API_KEY` | API key for LLM provider | (required) |
| `LLM_MODEL` | Model to use | gpt-4 |
| `LLM_MAX_TOKENS` | Max tokens per request | 1000 |
| `RATE_LIMIT_REQUESTS` | Requests per minute | 60 |
| `LOG_LEVEL` | Logging level | INFO |

## LLM Integration

The template includes patterns for:

### Basic Completion
```python
from app.llm.client import get_completion

response = await get_completion(
    prompt="Summarize this text",
    user_input=user_text,
    max_tokens=500
)
```

### With Safety Checks
```python
from app.llm.safety import sanitize_input, validate_output

# Sanitize user input
safe_input = sanitize_input(user_input)

# Get completion
response = await get_completion(prompt, safe_input)

# Validate output
validated = validate_output(response, expected_schema)
```

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app
```

## Deployment

Build Docker image:
```bash
docker build -t my-ai-service .
```

Run container:
```bash
docker run -p 8000:8000 --env-file .env my-ai-service
```

## Next Steps

1. Add your requirements to `sdlc_artifacts/requirements/`
2. Run the bootstrap prompt in Cursor
3. Follow the SDLC phases to build your service

