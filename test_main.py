from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_hello_world():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"text":"hello world"}

def test_health():

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status" : "ok"}


@patch("main.collection")
def test_add_repair_record(mock_collection):
    response = client.post(
        "/repair-history/add",
        json={
            "id": "1",
            "vehicle_id": 2,
            "text": "changed engine oil"
        })
    assert response.status_code == 200

    mock_collection.add.assert_called_once_with(
        documents=["changed engine oil"],
        ids=["1"],
        metadatas=[{"vehicle_id": 2}]
    )



