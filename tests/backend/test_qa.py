from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token():
    response = client.post("/api/authentication/authenticate", data={
        "username": "learner1",
        "password": "pass123"
    })
    return response.json()["access_token"]

def test_query_answer():
    token = get_token()
    response = client.post("/api/chatbot/query", headers={
        "Authorization": f"Bearer {token}"
    }, json={"query": "What is nuclear energy?"})
    assert response.status_code == 200
    assert "answer" in response.json()
