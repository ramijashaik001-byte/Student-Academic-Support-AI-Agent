import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ticket_creation_and_faculty_reply_workflow():
    # 1. Student creates ticket
    s_tok = client.post("/api/auth/login", json={
        "email": "ramija.student@campus.edu",
        "password": "Student@123"
    }).json()["access_token"]
    s_headers = {"Authorization": f"Bearer {s_tok}"}

    create_res = client.post("/api/tickets", json={
        "subject": "Need lab test date rescheduling due to medical reason",
        "description": "I have a scheduled hospital appointment on October 26.",
        "priority": "high"
    }, headers=s_headers)
    assert create_res.status_code == 200
    ticket_data = create_res.json()
    ticket_id = ticket_data["id"]
    assert ticket_data["ticket_number"].startswith("TICK-2026-")

    # 2. Faculty views and replies to ticket
    f_tok = client.post("/api/auth/login", json={
        "email": "prof.sharma@campus.edu",
        "password": "Faculty@123"
    }).json()["access_token"]
    f_headers = {"Authorization": f"Bearer {f_tok}"}

    reply_res = client.post(f"/api/tickets/{ticket_id}/messages", json={
        "message": "Please submit your hospital slip to the department office to approve rescheduling."
    }, headers=f_headers)
    assert reply_res.status_code == 200

    # 3. Faculty marks status as Resolved
    status_res = client.patch(f"/api/tickets/{ticket_id}/status", json={
        "status": "resolved"
    }, headers=f_headers)
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "resolved"

    # 4. Student checks in-app notifications
    notif_res = client.get("/api/notifications", headers=s_headers)
    assert notif_res.status_code == 200
    notifs = notif_res.json()
    assert len(notifs) > 0
    latest = notifs[0]
    assert "Ticket" in latest["title"] or "ticket" in latest["message"].lower()

    # 5. Student marks notification as read
    read_res = client.patch(f"/api/notifications/{latest['id']}/read", headers=s_headers)
    assert read_res.status_code == 200
