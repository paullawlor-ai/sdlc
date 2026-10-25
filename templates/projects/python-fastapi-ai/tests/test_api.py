"""API tests."""


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_readiness_check(client):
    """Test readiness check endpoint."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_complete_validation_error(client):
    """Test completion endpoint with invalid input."""
    response = client.post(
        "/api/v1/complete",
        json={"prompt": "", "max_tokens": 100},  # Empty prompt should fail
    )
    assert response.status_code == 422  # Validation error


def test_complete_max_tokens_validation(client):
    """Test completion endpoint with invalid max_tokens."""
    response = client.post(
        "/api/v1/complete",
        json={"prompt": "Hello", "max_tokens": 10000},  # Exceeds limit
    )
    assert response.status_code == 422  # Validation error
