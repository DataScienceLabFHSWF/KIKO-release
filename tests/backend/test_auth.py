from fastapi.testclient import TestClient
from fastapi import status
from app.main import app

client = TestClient(app)

def test_login_success():
    response = client.post("/api/authentication/authenticate", data={
        "username": "learner1",
        "password": "pass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure():
    response = client.post("/api/authentication/authenticate", data={
        "username": "learner1",
        "password": "pass123sss"
    })
    assert response.status_code == status.HTTP_404_NOT_FOUND
