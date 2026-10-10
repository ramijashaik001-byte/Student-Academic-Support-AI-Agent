import pytest
from app.database import SessionLocal
from app import models
from app.services.academic_tool_service import AcademicToolService
from app.ai.academic_intent_router import AcademicIntentRouter

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()

def test_semester_resolution():
    router = AcademicIntentRouter
    assert router.extract_semester("What are my 3-2 marks?") == "3-2"
    assert router.extract_semester("Show 1-1 results") == "1-1"
    assert router.extract_semester("Subjects in 2-1 semester") == "2-1"
    assert router.extract_semester("What is covered in first sem?") == "1-1"
    assert router.extract_semester("sixth sem timetable") == "3-2"
    assert router.extract_semester("general query without semester") is None

def test_curriculum_subjects_lookup(db_session):
    # Verify 1-1 subjects
    res_1_1 = AcademicToolService.get_semester_subjects(db_session, student_id=4, semester_label="1-1")
    assert res_1_1["total_subjects"] >= 8
    assert res_1_1["regulation"] == "R23"
    assert res_1_1["branch"] in ["ECE", "CSE"]
    assert res_1_1["verification_status"] == "Verified Official"
    codes = [s["code"] for s in res_1_1["subjects"]]
    assert any(c in codes for c in ["23BS1T01", "R23CC1101"])

    # Verify 3-1 core CSE / ECE subjects
    res_3_1 = AcademicToolService.get_semester_subjects(db_session, student_id=4, semester_label="3-1")
    codes_3_1 = [s["code"] for s in res_3_1["subjects"]]
    assert any(c in codes_3_1 for c in ["R23CC3107", "R23CC3101", "R23CS3104", "23EC3T01"])

def test_student_marks_retrieval_and_isolation(db_session):
    # Student 4 (Ramija Shaik) has verified 1-1 marks
    res = AcademicToolService.get_semester_marks(db_session, student_id=4, semester_label="1-1")
    assert res["records_found"] is True
    assert res["sgpa"] == 8.85
    assert len(res["subjects"]) > 0
    assert res["result_status"] == "PASSED"

    # Student 5 (Rahul Verma) has no 1-1 marks - honest explanation
    res_other = AcademicToolService.get_semester_marks(db_session, student_id=5, semester_label="1-1")
    assert res_other["records_found"] is False
    assert "I don't have your verified 1-1 results" in res_other["message"]

def test_missing_marksheet_honest_response(db_session):
    # Check semester 3-2 where no marks are uploaded yet
    res = AcademicToolService.get_semester_marks(db_session, student_id=4, semester_label="3-2")
    assert res["records_found"] is False
    assert "3-2" in res["message"]
    assert "Upload your marksheet" in res["message"]

def test_sgpa_calculation(db_session):
    res = AcademicToolService.calculate_sgpa(db_session, student_id=4, semester_label="1-1")
    assert res["success"] is True
    assert res["calculated_sgpa"] > 0
    assert "R23 Autonomous Scheme" in res["formula_used"]
    assert res["total_credits"] > 0

def test_cgpa_calculation(db_session):
    res = AcademicToolService.calculate_cgpa(db_session, student_id=4)
    assert res["success"] is True
    assert res["calculated_cgpa"] > 0
    assert "%" in res["equivalent_percentage"]
    assert res["total_semesters_completed"] >= 1

def test_supplementary_backlog_clearing(db_session):
    # Create synthetic test student profile clearly marked as TEST DATA
    test_user = db_session.query(models.User).filter(models.User.email == "synthetic.test@campus.edu").first()
    if not test_user:
        test_user = models.User(
            email="synthetic.test@campus.edu",
            hashed_password="test_hashed_password",
            full_name="Synthetic Test Student",
            role="student"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        test_profile = models.StudentProfile(
            user_id=test_user.id,
            roll_number="TEST-23471-SYNTHETIC",
            current_semester=3,
            academic_year="2023-2027",
            cgpa=7.5
        )
        db_session.add(test_profile)
        db_session.commit()
        db_session.refresh(test_profile)
    else:
        test_profile = test_user.student_profile

    # Create synthetic semester record
    sem_rec = models.StudentSemesterRecord(
        student_profile_id=test_profile.id,
        academic_year="2023-2024",
        semester_label="1-1",
        examination_session="Regular Dec 2023",
        result_status="PROMOTED_WITH_BACKLOGS"
    )
    db_session.add(sem_rec)
    db_session.commit()
    db_session.refresh(sem_rec)

    # Attempt 1: Failed in "SYNTH-101"
    att1 = models.StudentSubjectRecord(
        semester_record_id=sem_rec.id,
        student_profile_id=test_profile.id,
        subject_code="SYNTH-101",
        subject_name="Test Engineering Subject",
        credits=3.0,
        internal_marks=18.0,
        external_marks=15.0,
        total_marks=33.0,
        grade="F",
        grade_points=0,
        pass_fail_status="FAIL",
        is_backlog=True,
        attempt_number=1,
        exam_session="Regular Dec 2023"
    )
    db_session.add(att1)
    db_session.commit()

    # Verify that backlogs tool shows 1 active backlog
    backlog_check_1 = AcademicToolService.get_backlogs(db_session, test_user.id)
    assert backlog_check_1["total_active_backlogs"] == 1

    # Attempt 2: Supplementary examination passed
    att2 = models.StudentSubjectRecord(
        semester_record_id=sem_rec.id,
        student_profile_id=test_profile.id,
        subject_code="SYNTH-101",
        subject_name="Test Engineering Subject",
        credits=3.0,
        internal_marks=18.0,
        external_marks=45.0,
        total_marks=63.0,
        grade="C",
        grade_points=7,
        pass_fail_status="PASS",
        is_backlog=False,
        attempt_number=2,
        exam_session="Supplementary July 2024"
    )
    db_session.add(att2)
    db_session.commit()

    # Crucial acceptance test: cleared backlog must NOT count as active backlog!
    backlog_check_2 = AcademicToolService.get_backlogs(db_session, test_user.id)
    assert backlog_check_2["total_active_backlogs"] == 0
    assert backlog_check_2["total_cleared_backlogs"] == 1

    # Clean up synthetic test records
    db_session.query(models.StudentSubjectRecord).filter(models.StudentSubjectRecord.student_profile_id == test_profile.id).delete()
    db_session.query(models.StudentSemesterRecord).filter(models.StudentSemesterRecord.student_profile_id == test_profile.id).delete()
    db_session.query(models.StudentProfile).filter(models.StudentProfile.id == test_profile.id).delete()
    db_session.query(models.User).filter(models.User.id == test_user.id).delete()
    db_session.commit()

def test_attendance_calculation(db_session):
    res = AcademicToolService.get_attendance(db_session, student_id=4)
    assert res["records_found"] is True
    assert res["aggregate_percentage"] > 75.0
    assert res["standing"] == "ELIGIBLE"
    assert len(res["subjects"]) > 0

def test_academic_rules_retrieval():
    # Passing rules
    pass_rules = AcademicToolService.search_academic_rules("passing criteria")
    assert "35%" in pass_rules["rule"]["external_minimum"]
    assert "40%" in pass_rules["rule"]["aggregate_minimum"]

    # Attendance rules
    att_rules = AcademicToolService.search_academic_rules("attendance minimum")
    assert "75%" in att_rules["rule"]["minimum_aggregate"]
    assert "65%" in att_rules["rule"]["condonation_range"]

def test_academic_intent_router(db_session):
    # Marks query
    res_marks = AcademicIntentRouter.try_handle_academic_query(
        db_session, student_id=4, query="What are my 1-1 semester marks?",
        conversation_history=[], user_name="Ramija Shaik"
    )
    assert res_marks is not None
    assert "8.85" in res_marks["content"]

    # Missing marks query
    res_missing = AcademicIntentRouter.try_handle_academic_query(
        db_session, student_id=4, query="What are my 3-2 semester marks?",
        conversation_history=[], user_name="Ramija Shaik"
    )
    assert res_missing is not None
    assert "don't have your verified **3-2** marksheet" in res_missing["content"]

    # Ambiguous unit query
    res_ambiguous = AcademicIntentRouter.try_handle_academic_query(
        db_session, student_id=4, query="Explain Unit 3",
        conversation_history=[], user_name="Ramija Shaik"
    )
    assert res_ambiguous is not None
    assert "Which subject should I explain Unit 3 for?" in res_ambiguous["content"]

    # SGPA query
    res_sgpa = AcademicIntentRouter.try_handle_academic_query(
        db_session, student_id=4, query="What is my 1-1 SGPA?",
        conversation_history=[], user_name="Ramija Shaik"
    )
    assert res_sgpa is not None
    assert "SGPA" in res_sgpa["content"]

    # Passing rule query
    res_rule = AcademicIntentRouter.try_handle_academic_query(
        db_session, student_id=4, query="What is the passing rule?",
        conversation_history=[], user_name="Ramija Shaik"
    )
    assert res_rule is not None
    assert "35%" in res_rule["content"]
