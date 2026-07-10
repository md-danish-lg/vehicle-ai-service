from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_hello_world():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"text":"hello world"}

def test_health():

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status" : "ok"}




