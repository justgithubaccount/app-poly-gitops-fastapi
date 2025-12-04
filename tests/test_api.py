"""API endpoint tests."""


def test_health_endpoint(client):
    """Test GET /health returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint(client):
    """Test GET / returns service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "Chat Microservice"
    assert "version" in data


def test_chat_endpoint(client, mock_openrouter):
    """Test POST /api/v1/chat with mocked LLM."""
    response = client.post("/api/v1/chat", json={
        "messages": [{"role": "user", "content": "test"}]
    })
    assert response.status_code == 200
    assert "reply" in response.json()


def test_chat_endpoint_empty_messages(client, mock_openrouter):
    """Test POST /api/v1/chat with empty messages list."""
    response = client.post("/api/v1/chat", json={
        "messages": []
    })
    # Should still work, service handles empty messages
    assert response.status_code in (200, 422)


def test_create_project(client):
    """Test POST /api/v1/projects creates a project."""
    response = client.post("/api/v1/projects", json={
        "name": "Test Project"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data


def test_list_projects(client):
    """Test GET /api/v1/projects returns list."""
    # Create a project first
    client.post("/api/v1/projects", json={"name": "Test"})

    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_chat_in_project(client, mock_openrouter):
    """Test POST /api/v1/projects/{id}/chat."""
    # Create project
    create_resp = client.post("/api/v1/projects", json={"name": "Chat Test"})
    project_id = create_resp.json()["id"]

    # Chat in project
    response = client.post(f"/api/v1/projects/{project_id}/chat", json={
        "messages": [{"role": "user", "content": "hello"}]
    })
    assert response.status_code == 200
    assert "reply" in response.json()


def test_chat_in_nonexistent_project(client, mock_openrouter):
    """Test chat in non-existent project returns 404."""
    response = client.post("/api/v1/projects/nonexistent-id/chat", json={
        "messages": [{"role": "user", "content": "hello"}]
    })
    assert response.status_code == 404


def test_project_history(client, mock_openrouter):
    """Test GET /api/v1/projects/{id}/history."""
    # Create project
    create_resp = client.post("/api/v1/projects", json={"name": "History Test"})
    project_id = create_resp.json()["id"]

    # Send a message
    client.post(f"/api/v1/projects/{project_id}/chat", json={
        "messages": [{"role": "user", "content": "test message"}]
    })

    # Get history
    response = client.get(f"/api/v1/projects/{project_id}/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_behavior_schema_not_loaded(client):
    """Test GET /api/v1/behavior/schema when behavior not loaded."""
    response = client.get("/api/v1/behavior/schema")
    # Should return 404 when no Notion config
    assert response.status_code == 404
