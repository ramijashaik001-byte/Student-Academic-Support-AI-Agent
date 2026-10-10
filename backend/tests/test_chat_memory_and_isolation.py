import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_follow_up_and_memory():
    # 1. Login as Student
    login_res = client.post("/api/auth/login", json={
        "email": "ramija.student@campus.edu",
        "password": "Student@123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Ask first question: "Explain attendance rules"
    res1 = client.post("/api/chat", json={
        "message": "Explain the official university attendance rules"
    }, headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert "75%" in data1["content"]
    conv_id = data1["conversation_id"]

    # 3. Ask follow-up in the same conversation: "What if I have 72%?"
    res2 = client.post("/api/chat", json={
        "message": "What if I have 72%?",
        "conversation_id": conv_id
    }, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    # Must identify condonation bracket from context
    assert "72%" in data2["content"]
    assert "condonation" in data2["content"].lower()


def test_conversation_student_isolation():
    # Student 1: Ramija
    tok1 = client.post("/api/auth/login", json={
        "email": "ramija.student@campus.edu",
        "password": "Student@123"
    }).json()["access_token"]

    # Student 2: Rahul
    tok2 = client.post("/api/auth/login", json={
        "email": "rahul.student@campus.edu",
        "password": "Student@123"
    }).json()["access_token"]

    # Ramija creates a conversation
    c_res = client.post("/api/chat", json={
        "message": "Private question about my grades"
    }, headers={"Authorization": f"Bearer {tok1}"})
    conv_id = c_res.json()["conversation_id"]

    # Rahul attempts to fetch Ramija's conversation
    h_rahul = {"Authorization": f"Bearer {tok2}"}
    forbidden_res = client.get(f"/api/chat/conversations/{conv_id}", headers=h_rahul)
    assert forbidden_res.status_code == 404
