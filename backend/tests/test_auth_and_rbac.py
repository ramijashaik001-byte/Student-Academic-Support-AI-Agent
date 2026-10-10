import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import get_password_hash, create_access_token

client = TestClient(app)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"


def test_login_success():
    res = client.post("/api/auth/login", json={
        "email": "ramija.student@campus.edu",
        "password": "Student@123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "student"
    assert data["user"]["full_name"] == "Ramija Shaik"


def test_login_invalid_password():
    res = client.post("/api/auth/login", json={
        "email": "ramija.student@campus.edu",
        "password": "WrongPassword!99"
    })
    assert res.status_code == 401


def test_switch_demo_user():
    # Switch to faculty
    res = client.post("/api/auth/switch-demo?role=faculty")
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["role"] == "faculty"

    # Switch to admin
    res = client.post("/api/auth/switch-demo?role=admin")
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["role"] == "admin"


def test_rbac_admin_endpoint_forbidden_for_student():
    # Login as student
    login_res = client.post("/api/auth/login", json={
        "email": "ramija.student@campus.edu",
        "password": "Student@123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try to access admin analytics
    res = client.get("/api/admin/analytics", headers=headers)
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]


def test_rbac_admin_endpoint_allowed_for_admin():
    # Login as admin
    login_res = client.post("/api/auth/login", json={
        "email": "admin@campus.edu",
        "password": "Admin@123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/admin/analytics", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data
    assert "citation_rate_percentage" in data
