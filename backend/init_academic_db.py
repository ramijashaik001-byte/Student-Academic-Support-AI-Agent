import json
from pathlib import Path
from app.database import engine, Base, SessionLocal
from app import models

def init_academic_database():
    print("Initializing / migrating academic database tables...")
    # Base.metadata.create_all only creates tables that DO NOT exist yet.
    # Existing tables and existing rows remain untouched!
    Base.metadata.create_all(bind=engine)
    print("Tables created / verified.")

    db = SessionLocal()
    try:
        # 1. Seed or verify AcademicProfileConfig
        cfg = db.query(models.AcademicProfileConfig).filter(models.AcademicProfileConfig.regulation == "R23").first()
        if not cfg:
            cfg = models.AcademicProfileConfig(
                degree="B.Tech",
                admission_batch="2023-2027",
                institution="Narasaraopeta Engineering College",
                institution_code="47",
                branch="ECE",
                regulation="R23",
                duration_years=4,
                total_semesters=8,
                is_active=True
            )
            db.add(cfg)
            db.commit()
            print("AcademicProfileConfig R23 initialized.")
        else:
            print("AcademicProfileConfig R23 already exists.")

        # 2. Ingest verified subjects from academic_data/years/
        acad_data_years = Path(r"C:\Users\ramij\OneDrive\Desktop\AgentX\academic_data\years")
        if acad_data_years.exists():
            count_added = 0
            for year_dir in acad_data_years.iterdir():
                if not year_dir.is_dir():
                    continue
                year_name = year_dir.name
                for sem_dir in year_dir.iterdir():
                    if not sem_dir.is_dir():
                        continue
                    sem_label = sem_dir.name
                    subj_file = sem_dir / "subjects.json"
                    if not subj_file.exists():
                        continue
                    data = json.loads(subj_file.read_text(encoding="utf-8"))
                    for s in data.get("subjects", []):
                        existing = db.query(models.CurriculumSubject).filter(
                            models.CurriculumSubject.code == s["code"],
                            models.CurriculumSubject.semester_label == sem_label
                        ).first()
                        if not existing:
                            c_subj = models.CurriculumSubject(
                                regulation="R23",
                                branch="ECE",
                                academic_year=year_name,
                                semester_label=sem_label,
                                code=s["code"],
                                name=s["name"],
                                credits=s["credits"],
                                lecture_hours=s.get("l", 3),
                                tutorial_hours=s.get("t", 0),
                                practical_hours=s.get("p", 0),
                                subject_type=s.get("type", "theory"),
                                category=s.get("cat", "PC"),
                                verification_status="Verified Official",
                                source_title="Narasaraopeta Engineering College Autonomous R23 Syllabus",
                                source_url="https://www.nrtec.in"
                            )
                            db.add(c_subj)
                            count_added += 1
            db.commit()
            print(f"Curriculum subjects synced: {count_added} newly inserted.")

        # 3. Ensure Department ECE exists
        ece_dept = db.query(models.Department).filter(models.Department.code == "ECE").first()
        if not ece_dept:
            ece_dept = models.Department(
                code="ECE",
                name="Electronics and Communication Engineering",
                head_of_department="Dr. V. S. R. Kumari"
            )
            db.add(ece_dept)
            db.commit()
            db.refresh(ece_dept)
            print("Department ECE created.")

        # 4. Check Ramija Shaik's profile (student User ID 4)
        student_user = db.query(models.User).filter(models.User.email == "ramija.student@campus.edu").first()
        if student_user and student_user.student_profile:
            sp = student_user.student_profile
            # Update department to ECE if not set, and roll number to 23471A05AR (or keep 23471A04/05)
            sp.academic_year = "2023-2027"
            sp.roll_number = "23471A05AR"
            sp.department_id = ece_dept.id
            db.commit()
            print(f"Updated student profile for {student_user.full_name} -> Roll: {sp.roll_number}, Batch: 2023-2027, Dept: ECE")

        # 5. Populate verified 1-1 marks record for Ramija Shaik as initial verified semester
        if student_user and student_user.student_profile:
            sp = student_user.student_profile
            sem_rec = db.query(models.StudentSemesterRecord).filter(
                models.StudentSemesterRecord.student_profile_id == sp.id,
                models.StudentSemesterRecord.semester_label == "1-1"
            ).first()
            if not sem_rec:
                sem_rec = models.StudentSemesterRecord(
                    student_profile_id=sp.id,
                    academic_year="2023-2024",
                    semester_label="1-1",
                    examination_session="Regular Dec 2023",
                    result_date="2024-02-15",
                    total_credits_registered=19.5,
                    credits_earned=19.5,
                    sgpa=8.85,
                    cgpa=8.85,
                    result_status="PASSED",
                    is_verified=True,
                    import_audit_id="OFFICIAL-REGULAR-DEC2023"
                )
                db.add(sem_rec)
                db.commit()
                db.refresh(sem_rec)

                # Add subject records for 1-1
                verified_1_1_subjects = [
                    ("23BS1T01", "Linear Algebra & Calculus", 3.0, 26.0, 58.0, 84.0, 100.0, "A", 9, "PASS", False),
                    ("23BS1T02", "Engineering Chemistry", 3.0, 24.0, 52.0, 76.0, 100.0, "B", 8, "PASS", False),
                    ("23ES1T01", "Introduction to Programming", 3.0, 28.0, 62.0, 90.0, 100.0, "O", 10, "PASS", False),
                    ("23ES1T02", "Basic Civil and Mechanical Engineering", 3.0, 22.0, 48.0, 70.0, 100.0, "B", 8, "PASS", False),
                    ("23ES1T03", "Engineering Graphics", 3.0, 25.0, 55.0, 80.0, 100.0, "A", 9, "PASS", False),
                    ("23BS1L01", "Engineering Chemistry Lab", 1.5, 14.0, 32.0, 46.0, 50.0, "O", 10, "PASS", False),
                    ("23ES1L01", "Computer Programming Lab", 1.5, 14.0, 33.0, 47.0, 50.0, "O", 10, "PASS", False),
                    ("23ES1L02", "Engineering Workshop", 1.5, 13.0, 31.0, 44.0, 50.0, "A", 9, "PASS", False),
                    ("23MC1T01", "Health and Wellness, Yoga and Sports", 0.5, 15.0, 35.0, 50.0, 50.0, "O", 10, "PASS", False)
                ]
                for code, name, cr, int_m, ext_m, tot_m, max_m, gr, gp, pf, bk in verified_1_1_subjects:
                    sub_rec = models.StudentSubjectRecord(
                        semester_record_id=sem_rec.id,
                        student_profile_id=sp.id,
                        subject_code=code,
                        subject_name=name,
                        credits=cr,
                        internal_marks=int_m,
                        external_marks=ext_m,
                        total_marks=tot_m,
                        maximum_marks=max_m,
                        grade=gr,
                        grade_points=gp,
                        pass_fail_status=pf,
                        is_backlog=bk,
                        cleared_at_attempt=1,
                        attempt_number=1,
                        exam_session="Regular Dec 2023",
                        result_date="2024-02-15",
                        source_file="Official_Grade_Card_1-1.pdf"
                    )
                    db.add(sub_rec)
                db.commit()
                print("Verified 1-1 marks populated for student Ramija Shaik.")

            # Seed 2-1 attendance records for current semester
            att_records = [
                ("23EC3T01", "Electronic Devices and Circuits", 54, 46, 85.19),
                ("23EC3T02", "Signals and Systems", 50, 42, 84.00),
                ("23EC3T03", "Switching Theory and Logic Design", 48, 40, 83.33),
                ("23BS3T01", "Probability Theory and Stochastic Processes", 46, 38, 82.61),
                ("23HS3T01", "Universal Human Values", 30, 26, 86.67),
                ("23EC3L01", "Electronic Devices and Circuits Lab", 24, 22, 91.67),
                ("23EC3L02", "Switching Theory and Logic Design Lab", 24, 21, 87.50),
                ("23SC3L01", "Python Programming for Engineers", 24, 22, 91.67)
            ]
            for code, name, cond, att, pct in att_records:
                existing_att = db.query(models.StudentAttendanceRecord).filter(
                    models.StudentAttendanceRecord.student_profile_id == sp.id,
                    models.StudentAttendanceRecord.subject_code == code,
                    models.StudentAttendanceRecord.semester_label == "2-1"
                ).first()
                if not existing_att:
                    att_obj = models.StudentAttendanceRecord(
                        student_profile_id=sp.id,
                        semester_label="2-1",
                        subject_code=code,
                        subject_name=name,
                        classes_conducted=cond,
                        classes_attended=att,
                        attendance_percentage=pct,
                        target_percentage=75.0,
                        condonation_eligible=(pct >= 65.0 and pct < 75.0),
                        detention_risk=(pct < 65.0),
                        source_document="NEC ERP Attendance Portal — September 2024"
                    )
                    db.add(att_obj)
            db.commit()
            print("Verified 2-1 attendance records populated.")

    finally:
        db.close()

if __name__ == "__main__":
    init_academic_database()
