import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import create_access_token

client = TestClient(app)

@pytest.fixture
def student_auth_headers():
    token = create_access_token(subject=4, role="student")
    return {"Authorization": f"Bearer {token}"}

def test_download_marks_template():
    response = client.get("/api/academic/templates/marks")
    assert response.status_code == 200
    assert "subject_code" in response.text
    assert "internal_marks" in response.text

def test_download_attendance_template():
    response = client.get("/api/academic/templates/attendance")
    assert response.status_code == 200
    assert "classes_conducted" in response.text
    assert "attendance_percentage" in response.text

def test_validate_and_confirm_marks_csv(student_auth_headers):
    # Prepare valid CSV content for a test semester (e.g., 2-2)
    csv_content = (
        "subject_code,subject_name,credits,internal_marks,external_marks,total_marks,maximum_marks,grade,grade_points,result_status,attempt_number\n"
        "23EC4T01,Electronic Circuit Analysis,3.0,26,55,81,100,A,9,PASS,1\n"
        "23EC4T02,Analog Communications,3.0,24,56,80,100,A,9,PASS,1\n"
        "23EC4T03,Linear Control Systems,3.0,28,60,88,100,A,9,PASS,1\n"
        "23EC4T04,Electromagnetic Waves and Transmission Lines,3.0,25,52,77,100,B,8,PASS,1\n"
        "23HS4T01,Managerial Economics,3.0,27,58,85,100,A,9,PASS,1\n"
    )
    files = {
        "file": ("test_2_2_marks.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
    }
    data = {
        "semester_label": "2-2",
        "academic_year": "2024-2025",
        "session_title": "Regular May 2025"
    }

    # 1. Test validation endpoint
    val_resp = client.post(
        "/api/academic/import/marks-csv",
        headers=student_auth_headers,
        data=data,
        files=files
    )
    assert val_resp.status_code == 200
    val_data = val_resp.json()
    assert val_data["total_parsed_subjects"] == 5
    assert val_data["computed_sgpa"] > 8.0
    assert val_data["can_confirm"] is True

    # 2. Test confirmation endpoint
    confirm_resp = client.post(
        "/api/academic/import/confirm-marks",
        headers=student_auth_headers,
        json=val_data
    )
    assert confirm_resp.status_code == 200
    confirm_data = confirm_resp.json()
    assert confirm_data["success"] is True

    # 3. Verify that student marks query now reflects 2-2 marks
    marks_resp = client.get(
        "/api/academic/student/marks?semester=2-2",
        headers=student_auth_headers
    )
    assert marks_resp.status_code == 200
    m_data = marks_resp.json()
    assert m_data["records_found"] is True
    assert len(m_data["subjects"]) == 5

def test_invalid_file_extension_rejection(student_auth_headers):
    files = {
        "file": ("invalid_file.txt", io.BytesIO(b"dummy text"), "text/plain")
    }
    data = {"semester_label": "1-1"}
    resp = client.post(
        "/api/academic/import/marks-csv",
        headers=student_auth_headers,
        data=data,
        files=files
    )
    assert resp.status_code == 400
    assert "Only CSV files" in resp.json()["detail"]
