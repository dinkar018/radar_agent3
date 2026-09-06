"""
Integration tests for FastAPI REST API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_data_files(client):
    response = client.get("/api/data/files")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_kb_documents(client):
    response = client.get("/api/kb/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_experiments(client):
    response = client.get("/api/experiments/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
