from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

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

@patch("main.collection")
def test_search_repair_record(mock_collection):

    mock_collection.query.return_value ={
        "ids": [["1"]],
        "documents": [["changed engine oil"]],
        "metadatas": [[{"vehicle_id": 2 }]]
    }


    response = client.post(
        "/repair-history/search",
        json={
            "vehicle_id": 2,
            "text": "engine oil",
            "result_length": 3
        }
        
    )

    assert response.status_code == 200

    assert response.json() == {
        "result": ["changed engine oil"]
    }


    mock_collection.query.assert_called_once_with(
        query_texts=["engine oil"],
        where={"vehicle_id":2 },
        n_results=3
    )


@patch("main.llm_client")
@patch("main.collection")
def test_summarize_success(mock_collection, mock_llm):
    mock_collection.query.return_value = {
        "documents": [[
            "Changed engine oil",
            "Replaced brake pads"
        ]]
    }


    mock_summary = MagicMock()
    mock_summary.choices =[
        MagicMock(
            message=MagicMock(
                content="The vehicle received an oil change and brake replacement."
            )
        )
    ]

    mock_llm.chat.completions.create.return_value = mock_summary


    response = client.post(
        "/repair-history/summarize",
        json={
            "text": "Summarize repairs",
            "vehicle_id": 1,
            "result_length": 2
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "summary": "The vehicle received an oil change and brake replacement.",
        "records_used": 2
    }

    mock_collection.query.assert_called_once()
    mock_llm.chat.completions.create.assert_called_once()



@patch("main.collection")
def test_summarize_not_found(mock_collection):

    mock_collection.query.return_value = {
        "documents": [[]]
    }


    response = client.post(
        "/repair-history/summarize",
        json={
            "text":"repair history",
            "vehicle_id":2,
            "result_length":3
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Repair History Not Found"

    