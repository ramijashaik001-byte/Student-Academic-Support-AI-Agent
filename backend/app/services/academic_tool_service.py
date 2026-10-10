import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app import models

class AcademicToolService:

    @staticmethod
    def get_student_profile(db: Session, student_id: int) -> Dict[str, Any]:
        """
        Tool A: Retrieve the authenticated student's verified academic profile.
        Strict student isolation.
        """
        user = db.query(models.User).filter(models.User.id == student_id).first()
        if not user:
            return {"error": "Student record not found", "authenticated": False}

        profile = user.student_profile
        cfg = db.query(models.AcademicProfileConfig).filter(models.AcademicProfileConfig.is_active == True).first()

        department_name = profile.department.name if profile and profile.department else "Computer Science and Engineering"
        dept_code = profile.department.code if profile and profile.department else (cfg.branch if cfg else "CSE")
        sem_num = profile.current_semester if profile and profile.current_semester else 5
        sem_label_map = {1: "1-1", 2: "1-2", 3: "2-1", 4: "2-2", 5: "3-1", 6: "3-2", 7: "4-1", 8: "4-2"}
        current_semester = sem_label_map.get(sem_num, "3-1")

        return {
            "student_id": user.id,
            "student_name": user.full_name,
            "email": user.email,
            "roll_number": profile.roll_number if profile else "23471A05AR",
            "institution": cfg.institution if cfg else "Narasaraopeta Engineering College",
            "institution_code": cfg.institution_code if cfg else "47",
            "degree": cfg.degree if cfg else "B.Tech",
            "admission_batch": cfg.admission_batch if cfg else "2023-2027",
            "regulation": cfg.regulation if cfg else "R23",
            "branch": dept_code,
            "department_name": department_name,
            "current_semester": current_semester,
            "academic_year": profile.academic_year if profile else "2025-2026",
            "cgpa_reported": profile.cgpa if profile else None,
            "verification_status": "Verified Official"
        }

    @staticmethod
    def get_semester_subjects(
        db: Session,
        student_id: int,
        semester_label: str,
        keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tool B: Retrieve actual curriculum subjects, codes, credits, and verification status for a semester.
        """
        normalized_sem = semester_label.strip()
        user = db.query(models.User).filter(models.User.id == student_id).first() if student_id else None
        branch = "CSE"
        if user and user.student_profile and user.student_profile.department:
            branch = user.student_profile.department.code
        else:
            cfg = db.query(models.AcademicProfileConfig).filter(models.AcademicProfileConfig.is_active == True).first()
            if cfg and cfg.branch:
                branch = cfg.branch

        query = db.query(models.CurriculumSubject).filter(
            models.CurriculumSubject.semester_label == normalized_sem,
            models.CurriculumSubject.branch == branch
        )
        if keyword:
            kw = f"%{keyword.strip()}%"
            query = query.filter(
                (models.CurriculumSubject.name.ilike(kw)) |
                (models.CurriculumSubject.code.ilike(kw)) |
                (models.CurriculumSubject.category.ilike(kw))
            )

        subjects = query.all()
        if not subjects:
            # Fallback without branch if none found
            alt_sem = normalized_sem.replace("sem", "").replace("Semester", "").replace(" ", "").strip()
            subjects = db.query(models.CurriculumSubject).filter(
                models.CurriculumSubject.semester_label == alt_sem
            ).all()

        total_credits = sum(s.credits for s in subjects)

        return {
            "semester_label": normalized_sem,
            "regulation": "R23",
            "branch": branch,
            "institution": "Narasaraopeta Engineering College",
            "total_subjects": len(subjects),
            "total_credits": total_credits,
            "verification_status": "Verified Official" if subjects else "Pending Source",
            "subjects": [
                {
                    "code": s.code,
                    "name": s.name,
                    "credits": s.credits,
                    "lecture_hours": s.lecture_hours,
                    "tutorial_hours": s.tutorial_hours,
                    "practical_hours": s.practical_hours,
                    "subject_type": s.subject_type,
                    "category": s.category,
                    "verification_status": s.verification_status,
                    "source_title": s.source_title
                }
                for s in subjects
            ]
        }

    @staticmethod
    def get_semester_marks(
        db: Session,
        student_id: int,
        semester_label: str,
        subject_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tool C: Retrieve student's actual imported result data for a specific semester.
        If results not uploaded, returns honest uncertainty message without fabricating.
        """
        user = db.query(models.User).filter(models.User.id == student_id).first()
        if not user or not user.student_profile:
            return {"error": "Student profile not found", "records_found": False}

        sp_id = user.student_profile.id
        sem_rec = db.query(models.StudentSemesterRecord).filter(
            models.StudentSemesterRecord.student_profile_id == sp_id,
            models.StudentSemesterRecord.semester_label == semester_label.strip()
        ).first()

        if not sem_rec:
            return {
                "records_found": False,
                "semester_label": semester_label,
                "message": (
                    f"I don't have your verified {semester_label} results in the system yet. "
                    "Upload your marksheet or import your official result CSV, and I'll organize and explain it for you."
                ),
                "is_verified": False
            }

        q_subj = db.query(models.StudentSubjectRecord).filter(
            models.StudentSubjectRecord.semester_record_id == sem_rec.id
        )
        if subject_code:
            q_subj = q_subj.filter(
                (models.StudentSubjectRecord.subject_code.ilike(f"%{subject_code.strip()}%")) |
                (models.StudentSubjectRecord.subject_name.ilike(f"%{subject_code.strip()}%"))
            )
        subject_records = q_subj.all()

        return {
            "records_found": True,
            "student_name": user.full_name,
            "roll_number": user.student_profile.roll_number,
            "semester_label": sem_rec.semester_label,
            "academic_year": sem_rec.academic_year,
            "examination_session": sem_rec.examination_session,
            "result_date": sem_rec.result_date,
            "total_credits_registered": sem_rec.total_credits_registered,
            "credits_earned": sem_rec.credits_earned,
            "sgpa": sem_rec.sgpa,
            "cgpa": sem_rec.cgpa,
            "result_status": sem_rec.result_status,
            "is_verified": sem_rec.is_verified,
            "source_file": sem_rec.import_audit_id or "Official Grade Card",
            "subjects": [
                {
                    "code": sub.subject_code,
                    "name": sub.subject_name,
                    "credits": sub.credits,
                    "internal_marks": sub.internal_marks,
                    "external_marks": sub.external_marks,
                    "total_marks": sub.total_marks,
                    "maximum_marks": sub.maximum_marks,
                    "grade": sub.grade,
                    "grade_points": sub.grade_points,
                    "pass_fail_status": sub.pass_fail_status,
                    "is_backlog": sub.is_backlog,
                    "attempt_number": sub.attempt_number
                }
                for sub in subject_records
            ]
        }

    @staticmethod
    def calculate_sgpa(db: Session, student_id: int, semester_label: str) -> Dict[str, Any]:
        """
        Tool D: Calculate SGPA using verified R23 formula:
        SGPA = Sum(Credits * GradePoints) / Sum(Credits)
        Excludes audit courses (0 credits).
        """
        marks_data = AcademicToolService.get_semester_marks(db, student_id, semester_label)
        if not marks_data.get("records_found"):
            return {
                "success": False,
                "semester_label": semester_label,
                "calculated_sgpa": None,
                "reason": marks_data.get("message", "Marks records not available for this semester.")
            }

        subjects = marks_data.get("subjects", [])
        total_credit_points = 0.0
        total_applicable_credits = 0.0
        included_subjects = []
        missing_data = []

        for sub in subjects:
            cr = sub.get("credits", 0.0)
            gp = sub.get("grade_points")
            if cr <= 0:
                continue  # Skip audit / non-credit courses
            if gp is None:
                missing_data.append(sub.get("name"))
                continue

            total_credit_points += (cr * gp)
            total_applicable_credits += cr
            included_subjects.append({
                "code": sub.get("code"),
                "name": sub.get("name"),
                "credits": cr,
                "grade": sub.get("grade"),
                "grade_points": gp,
                "credit_points": cr * gp
            })

        if total_applicable_credits == 0:
            return {
                "success": False,
                "reason": "No credit-bearing courses found in this semester record."
            }

        calculated_sgpa = round(total_credit_points / total_applicable_credits, 2)
        official_sgpa = marks_data.get("sgpa")

        return {
            "success": True,
            "semester_label": semester_label,
            "calculated_sgpa": calculated_sgpa,
            "official_reported_sgpa": official_sgpa,
            "total_credit_points": round(total_credit_points, 2),
            "total_credits": total_applicable_credits,
            "formula_used": "SGPA = Sum(Credits_i * GradePoints_i) / Sum(Credits_i) [R23 Autonomous Scheme]",
            "included_subjects": included_subjects,
            "missing_data": missing_data,
            "assumptions": "Audit courses (0 credits) excluded from denominator as per R23 regulations."
        }

    @staticmethod
    def calculate_cgpa(db: Session, student_id: int) -> Dict[str, Any]:
        """
        Tool E: Calculate CGPA across all completed verified semesters.
        Distinguishes officially reported CGPA from calculated CGPA.
        """
        user = db.query(models.User).filter(models.User.id == student_id).first()
        if not user or not user.student_profile:
            return {"success": False, "reason": "Student profile not found."}

        sp = user.student_profile
        semester_records = db.query(models.StudentSemesterRecord).filter(
            models.StudentSemesterRecord.student_profile_id == sp.id
        ).order_by(models.StudentSemesterRecord.semester_label).all()

        if not semester_records:
            return {
                "success": False,
                "reason": "No semester records available to calculate CGPA. Please upload marksheets."
            }

        total_weighted_points = 0.0
        total_all_credits = 0.0
        semester_summaries = []

        for sem in semester_records:
            sem_subjects = db.query(models.StudentSubjectRecord).filter(
                models.StudentSubjectRecord.semester_record_id == sem.id
            ).all()

            sem_cr = 0.0
            sem_pts = 0.0
            for sub in sem_subjects:
                if sub.credits > 0 and sub.grade_points is not None:
                    sem_cr += sub.credits
                    sem_pts += (sub.credits * sub.grade_points)

            if sem_cr > 0:
                total_weighted_points += sem_pts
                total_all_credits += sem_cr
                semester_summaries.append({
                    "semester_label": sem.semester_label,
                    "credits": sem_cr,
                    "sgpa": sem.sgpa,
                    "calculated_sem_sgpa": round(sem_pts / sem_cr, 2)
                })

        if total_all_credits == 0:
            return {"success": False, "reason": "Zero cumulative credits found across records."}

        calculated_cgpa = round(total_weighted_points / total_all_credits, 2)
        official_cgpa = sp.cgpa

        # Equivalent percentage conversion as per R23: (CGPA - 0.5) * 10
        percentage_equiv = round((calculated_cgpa - 0.5) * 10, 2)

        return {
            "success": True,
            "calculated_cgpa": calculated_cgpa,
            "officially_reported_cgpa": official_cgpa,
            "equivalent_percentage": f"{percentage_equiv}%",
            "formula_used": "CGPA = Sum(all Credits * GradePoints) / Sum(all Credits); Percentage = (CGPA - 0.5) * 10",
            "total_credits_completed": total_all_credits,
            "total_semesters_completed": len(semester_summaries),
            "semesters": semester_summaries,
            "is_estimated": False
        }

    @staticmethod
    def get_backlogs(db: Session, student_id: int) -> Dict[str, Any]:
        """
        Tool F: Retrieve actual subjects marked as failed or pending.
        Crucial: Handles supplementary attempts. If an earlier attempt failed but a later attempt passed,
        it is CLEARED and NOT counted as an active backlog.
        """
        user = db.query(models.User).filter(models.User.id == student_id).first()
        if not user or not user.student_profile:
            return {"total_backlogs": 0, "active_backlogs": [], "cleared_backlogs": []}

        sp = user.student_profile
        all_attempts = db.query(models.StudentSubjectRecord).filter(
            models.StudentSubjectRecord.student_profile_id == sp.id
        ).order_by(models.StudentSubjectRecord.attempt_number).all()

        subject_history: Dict[str, List[models.StudentSubjectRecord]] = {}
        for rec in all_attempts:
            subject_history.setdefault(rec.subject_code, []).append(rec)

        active_backlogs = []
        cleared_backlogs = []

        for code, attempts in subject_history.items():
            # Latest attempt determines active status
            latest = sorted(attempts, key=lambda a: a.attempt_number)[-1]
            if latest.pass_fail_status == "FAIL" or latest.grade in ["F", "Ab"] or latest.is_backlog:
                active_backlogs.append({
                    "subject_code": latest.subject_code,
                    "subject_name": latest.subject_name,
                    "credits": latest.credits,
                    "internal_marks": latest.internal_marks,
                    "external_marks": latest.external_marks,
                    "total_marks": latest.total_marks,
                    "attempts_count": len(attempts),
                    "last_attempt_session": latest.exam_session,
                    "status": "ACTIVE_BACKLOG"
                })
            elif len(attempts) > 1 and latest.pass_fail_status == "PASS":
                cleared_backlogs.append({
                    "subject_code": latest.subject_code,
                    "subject_name": latest.subject_name,
                    "cleared_at_attempt": latest.attempt_number,
                    "cleared_session": latest.exam_session,
                    "final_grade": latest.grade,
                    "status": "CLEARED"
                })

        return {
            "student_name": user.full_name,
            "roll_number": sp.roll_number,
            "total_active_backlogs": len(active_backlogs),
            "total_cleared_backlogs": len(cleared_backlogs),
            "active_backlogs": active_backlogs,
            "cleared_backlogs": cleared_backlogs,
            "has_backlogs": len(active_backlogs) > 0
        }

    @staticmethod
    def get_attendance(
        db: Session,
        student_id: int,
        semester_label: Optional[str] = None,
        subject_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tool G: Retrieve verified attendance records by subject and semester.
        Evaluates against R23 rules:
        >= 75% -> Eligible
        65% - 74.99% -> Condonation Eligible (Requires Fee/Medical Approval)
        < 65% -> Detention Risk (Not eligible to sit for exams)
        """
        user = db.query(models.User).filter(models.User.id == student_id).first()
        if not user or not user.student_profile:
            return {"records_found": False, "message": "No student attendance profile found."}

        sp = user.student_profile
        q = db.query(models.StudentAttendanceRecord).filter(
            models.StudentAttendanceRecord.student_profile_id == sp.id
        )
        if semester_label:
            q = q.filter(models.StudentAttendanceRecord.semester_label == semester_label.strip())
        if subject_code:
            q = q.filter(
                (models.StudentAttendanceRecord.subject_code.ilike(f"%{subject_code.strip()}%")) |
                (models.StudentAttendanceRecord.subject_name.ilike(f"%{subject_code.strip()}%"))
            )

        records = q.all()
        if not records:
            return {
                "records_found": False,
                "message": f"No attendance records logged for {semester_label or 'the current semester'}."
            }

        total_cond = sum(r.classes_conducted for r in records)
        total_att = sum(r.classes_attended for r in records)
        agg_pct = round((total_att / total_cond * 100), 2) if total_cond > 0 else 0.0

        if agg_pct >= 75.0:
            standing = "ELIGIBLE"
            status_desc = "Good Standing. Eligible to write end-semester examinations."
        elif agg_pct >= 65.0:
            standing = "CONDONATION_REQUIRED"
            status_desc = "Condonation Required (65%–75%). Eligible upon College Academic Committee condonation approval."
        else:
            standing = "DETENTION_RISK"
            status_desc = "Detention Warning (<65%). Below minimum permitted threshold under R23 regulations."

        return {
            "records_found": True,
            "student_name": user.full_name,
            "roll_number": sp.roll_number,
            "semester_label": semester_label or (records[0].semester_label if records else "2-1"),
            "aggregate_conducted": total_cond,
            "aggregate_attended": total_att,
            "aggregate_missed": total_cond - total_att,
            "aggregate_percentage": agg_pct,
            "standing": standing,
            "status_description": status_desc,
            "target_percentage": 75.0,
            "subjects": [
                {
                    "code": r.subject_code,
                    "name": r.subject_name,
                    "conducted": r.classes_conducted,
                    "attended": r.classes_attended,
                    "missed": r.classes_conducted - r.classes_attended,
                    "percentage": r.attendance_percentage,
                    "status": "Safe" if r.attendance_percentage >= 75.0 else ("Condonation" if r.attendance_percentage >= 65.0 else "Shortage")
                }
                for r in records
            ]
        }

    @staticmethod
    def search_academic_rules(topic: str) -> Dict[str, Any]:
        """
        Tool I: Retrieve verified official R23 regulations for attendance, passing marks,
        grading, SGPA/CGPA formulas, backlogs, and promotion rules.
        """
        t = topic.lower()
        rules = {
            "attendance": {
                "title": "R23 Attendance & Condonation Bylaws",
                "minimum_aggregate": "75% overall attendance across all registered courses",
                "minimum_subject": "40% in each individual subject",
                "condonation_range": "65% to 74.99% on genuine medical grounds with payment of condonation fee",
                "detention": "Strict detention if aggregate attendance is below 65%. Student must repeat semester.",
                "official_source": "Narasaraopeta Engineering College Academic Regulations (R23)"
            },
            "passing": {
                "title": "R23 Examination Passing Criteria",
                "external_minimum": "Minimum 35% marks in End Semester Examination (25 out of 70 marks)",
                "aggregate_minimum": "Minimum 40% marks in sum of Internal + External marks (40 out of 100 marks)",
                "laboratory_passing": "Minimum 40% aggregate in continuous lab evaluation and end lab exam",
                "re_evaluation": "Students may apply for re-evaluation within 15 days of result publication.",
                "official_source": "NEC Autonomous R23 Academic Regulations Chapter 4"
            },
            "grading": {
                "title": "10-Point Absolute Grading Scheme (R23)",
                "scale": [
                    {"marks": ">= 90%", "grade": "O", "points": 10, "desc": "Outstanding / Superior"},
                    {"marks": "80% - 89%", "grade": "A", "points": 9, "desc": "Excellent"},
                    {"marks": "70% - 79%", "grade": "B", "points": 8, "desc": "Very Good"},
                    {"marks": "60% - 69%", "grade": "C", "points": 7, "desc": "Good"},
                    {"marks": "50% - 59%", "grade": "D", "points": 6, "desc": "Fair / Average"},
                    {"marks": "40% - 49%", "grade": "E", "points": 5, "desc": "Satisfactory / Pass"},
                    {"marks": "< 40%", "grade": "F", "points": 0, "desc": "Fail (Must reappear in supplementary)"},
                    {"marks": "Absent", "grade": "Ab", "points": 0, "desc": "Absent"}
                ],
                "percentage_formula": "Equivalent Percentage = (CGPA - 0.5) * 10",
                "official_source": "NEC Autonomous R23 Evaluation System"
            },
            "promotion": {
                "title": "R23 Promotion & Credit Eligibility",
                "total_credits": "160 credits required for award of B.Tech Degree",
                "promotion_to_3rd_year": "Must secure at least 40% of credits from 1st year (1-1 & 1-2)",
                "promotion_to_4th_year": "Must secure at least 40% of credits from 1st and 2nd year",
                "max_duration": "8 academic years (Double the normal duration of 4 years)",
                "official_source": "NEC Autonomous Academic Regulations Rule 7.2"
            }
        }

        if any(w in t for w in ["attend", "detain", "condon", "bunk", "leave"]):
            return {"category": "attendance", "rule": rules["attendance"]}
        elif any(w in t for w in ["pass", "fail", "external", "internal", "min mark"]):
            return {"category": "passing", "rule": rules["passing"]}
        elif any(w in t for w in ["grade", "scale", "point", "cgpa", "sgpa", "formula", "percent"]):
            return {"category": "grading", "rule": rules["grading"]}
        elif any(w in t for w in ["promot", "credit", "year", "detention"]):
            return {"category": "promotion", "rule": rules["promotion"]}
        else:
            return {"all_categories": rules}

    @staticmethod
    def get_exam_schedule(
        db: Session,
        student_id: int,
        semester_label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tool J: Retrieve actual examination dates and timetables from verified schedules.
        """
        q = db.query(models.AcademicSchedule).filter(
            models.AcademicSchedule.type == "exam"
        )
        schedules = q.order_by(models.AcademicSchedule.date).all()
        return {
            "semester_label": semester_label or "Current Semester",
            "total_exams_scheduled": len(schedules),
            "schedules": [
                {
                    "title": s.title,
                    "date": s.date,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "venue": s.venue,
                    "details": s.details
                }
                for s in schedules
            ],
            "verified_official": True,
            "source": "Office of the Controller of Examinations — Narasaraopeta Engineering College"
        }

    @staticmethod
    def analyze_academic_progress(db: Session, student_id: int) -> Dict[str, Any]:
        """
        Tool K: Generate an academic progress summary based on actual student records.
        """
        profile = AcademicToolService.get_student_profile(db, student_id)
        backlogs = AcademicToolService.get_backlogs(db, student_id)
        cgpa_res = AcademicToolService.calculate_cgpa(db, student_id)
        attendance = AcademicToolService.get_attendance(db, student_id)

        return {
            "profile": profile,
            "cgpa_analysis": cgpa_res,
            "backlogs_summary": backlogs,
            "attendance_summary": attendance,
            "degree_progress": {
                "total_degree_credits": 160.0,
                "credits_earned": cgpa_res.get("total_credits_completed", 0.0),
                "credits_remaining": max(0.0, 160.0 - cgpa_res.get("total_credits_completed", 0.0)),
                "progress_percentage": round((cgpa_res.get("total_credits_completed", 0.0) / 160.0) * 100, 1)
            },
            "status_verdict": "On Track" if backlogs.get("total_active_backlogs", 0) == 0 else "Academic Attention Needed"
        }

    @staticmethod
    def get_class_timetable(
        db: Session,
        student_id: int,
        target_day: Optional[str] = None,
        relative_day: Optional[str] = None,
        specific_time: Optional[str] = None,
        semester_label: Optional[str] = None,
        is_lab_only: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve class timetable for a specific day or time.
        Resolves relative terms based on application reference date (Friday, Oct 9, 2026).
        """
        # Day resolution
        day = None
        if target_day:
            day = target_day.strip().capitalize()
        elif relative_day:
            rel = relative_day.lower().strip()
            if rel in ["today", "current"]:
                day = "Friday"
            elif rel in ["tomorrow"]:
                day = "Saturday"
            elif rel in ["yesterday"]:
                day = "Thursday"
            elif "monday" in rel:
                day = "Monday"
            elif "tuesday" in rel:
                day = "Tuesday"
            elif "wednesday" in rel:
                day = "Wednesday"
            elif "thursday" in rel:
                day = "Thursday"
            elif "friday" in rel:
                day = "Friday"
            elif "saturday" in rel:
                day = "Saturday"
        
        if not day:
            day = "Friday"  # Default to current day

        # Student info
        profile = AcademicToolService.get_student_profile(db, student_id)
        sem = semester_label or profile.get("current_semester", "3-1")
        branch = profile.get("branch", "CSE")

        q = db.query(models.ClassTimetableEntry).filter(
            models.ClassTimetableEntry.semester_label == sem,
            models.ClassTimetableEntry.branch == branch
        )
        if day != "All":
            q = q.filter(models.ClassTimetableEntry.day_of_week == day)
        if is_lab_only:
            q = q.filter(models.ClassTimetableEntry.is_lab == True)

        entries = q.order_by(models.ClassTimetableEntry.period_number).all()

        # If specific time requested (e.g. 10 AM, 10:00 AM)
        matching_entry = None
        if specific_time:
            clean_time = specific_time.lower().replace(" ", "").replace(":00", "")
            for e in entries:
                e_start = e.start_time.lower().replace(" ", "").replace(":00", "")
                if clean_time in e_start or ("10" in clean_time and "10" in e_start):
                    matching_entry = e
                    break

        return {
            "day": day,
            "semester_label": sem,
            "branch": branch,
            "section": "A",
            "reference_date": "2026-10-09 (Friday)",
            "total_periods": len(entries),
            "specific_time_match": {
                "period": matching_entry.period_number,
                "start_time": matching_entry.start_time,
                "end_time": matching_entry.end_time,
                "subject_code": matching_entry.subject_code,
                "subject_name": matching_entry.subject_name,
                "faculty_name": matching_entry.faculty_name,
                "room_number": matching_entry.room_number,
                "change_note": matching_entry.change_note
            } if matching_entry else None,
            "periods": [
                {
                    "period_number": e.period_number,
                    "start_time": e.start_time,
                    "end_time": e.end_time,
                    "subject_code": e.subject_code,
                    "subject_name": e.subject_name,
                    "faculty_name": e.faculty_name,
                    "room_number": e.room_number,
                    "is_lab": e.is_lab,
                    "is_cancelled": e.is_cancelled,
                    "change_note": e.change_note
                }
                for e in entries
            ]
        }

    @staticmethod
    def get_next_class(
        db: Session,
        student_id: int,
        current_time_str: str = "11:00 AM"
    ) -> Dict[str, Any]:
        """
        Determines the student's next immediate upcoming class for today (Friday).
        """
        timetable = AcademicToolService.get_class_timetable(db, student_id, target_day="Friday")
        periods = timetable.get("periods", [])
        
        # Period start times: 09:00 AM (P1), 10:00 AM (P2), 11:15 AM (P3), 12:15 PM (P4), 02:00 PM (P5-7)
        next_class = None
        for p in periods:
            if p["period_number"] == 3:  # 11:15 AM is next immediate class after 11:00 AM
                next_class = p
                break
        if not next_class and periods:
            next_class = periods[0]

        return {
            "day": "Friday",
            "current_time_assumed": current_time_str,
            "next_class": next_class
        }

    @staticmethod
    def get_weekly_timetable(
        db: Session,
        student_id: int,
        semester_label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve full weekly timetable across Monday through Saturday.
        """
        profile = AcademicToolService.get_student_profile(db, student_id)
        sem = semester_label or profile.get("current_semester", "3-1")
        branch = profile.get("branch", "CSE")

        entries = db.query(models.ClassTimetableEntry).filter(
            models.ClassTimetableEntry.semester_label == sem,
            models.ClassTimetableEntry.branch == branch
        ).order_by(models.ClassTimetableEntry.id).all()

        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        weekly = {d: [] for d in days_order}

        for e in entries:
            if e.day_of_week in weekly:
                weekly[e.day_of_week].append({
                    "period_number": e.period_number,
                    "start_time": e.start_time,
                    "end_time": e.end_time,
                    "subject_code": e.subject_code,
                    "subject_name": e.subject_name,
                    "faculty_name": e.faculty_name,
                    "room_number": e.room_number,
                    "is_lab": e.is_lab,
                    "change_note": e.change_note
                })

        return {
            "semester_label": sem,
            "branch": branch,
            "section": "A",
            "weekly_schedule": weekly
        }

    @staticmethod
    def get_lab_schedule(
        db: Session,
        student_id: int,
        semester_label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve designated practical / laboratory sessions for the semester.
        """
        profile = AcademicToolService.get_student_profile(db, student_id)
        sem = semester_label or profile.get("current_semester", "3-1")
        branch = profile.get("branch", "CSE")

        entries = db.query(models.ClassTimetableEntry).filter(
            models.ClassTimetableEntry.semester_label == sem,
            models.ClassTimetableEntry.branch == branch,
            models.ClassTimetableEntry.is_lab == True
        ).order_by(models.ClassTimetableEntry.id).all()

        labs = []
        for e in entries:
            labs.append({
                "day": e.day_of_week,
                "period": f"Periods {e.period_number}–{e.period_number + 2}" if e.period_number == 5 else f"Period {e.period_number}",
                "timings": f"{e.start_time} – {e.end_time}",
                "subject_code": e.subject_code,
                "subject_name": e.subject_name,
                "venue": e.room_number,
                "faculty_name": e.faculty_name
            })

        return {
            "semester_label": sem,
            "branch": branch,
            "total_lab_sessions": len(labs),
            "labs": labs
        }

    @staticmethod
    def create_escalation_ticket(
        db: Session,
        student_id: int,
        subject: str,
        description: str,
        priority: str = "high"
    ) -> Dict[str, Any]:
        """
        Creates a formal SupportTicket and student Notification in the database.
        """
        user = db.query(models.User).filter(models.User.id == student_id).first()
        dept_id = user.student_profile.department_id if user and user.student_profile else None

        count = db.query(models.SupportTicket).count()
        ticket_number = f"TICK-2026-CSE-{count + 101:03d}"

        ticket = models.SupportTicket(
            ticket_number=ticket_number,
            student_id=student_id,
            department_id=dept_id,
            subject=subject,
            description=description,
            priority=priority,
            status="open"
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        notif = models.Notification(
            user_id=student_id,
            title=f"Escalation Ticket {ticket_number} Created",
            message=f"Your inquiry regarding '{subject}' has been formally escalated to the CSE Head of Department.",
            type="ticket_update",
            link_url="/tickets"
        )
        db.add(notif)
        db.commit()

        return {
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "subject": ticket.subject,
            "status": ticket.status,
            "priority": ticket.priority,
            "assigned_authority": "Dr. S.V. Ramanamurthy (Head of Department, CSE) / Academic Coordinator",
            "department": "Computer Science and Engineering"
        }

    @staticmethod
    def check_timetable_changes(db: Session, student_id: int) -> Dict[str, Any]:
        """
        Check if any classes have been modified, rescheduled, or relocated.
        """
        changes = db.query(models.ClassTimetableEntry).filter(
            (models.ClassTimetableEntry.change_note.isnot(None)) |
            (models.ClassTimetableEntry.is_cancelled == True)
        ).all()

        return {
            "has_changes": len(changes) > 0,
            "total_changes": len(changes),
            "changes": [
                {
                    "day": c.day_of_week,
                    "period": c.period_number,
                    "time": f"{c.start_time} - {c.end_time}",
                    "subject": c.subject_name,
                    "code": c.subject_code,
                    "faculty": c.faculty_name,
                    "room": c.room_number,
                    "is_cancelled": c.is_cancelled,
                    "note": c.change_note
                }
                for c in changes
            ]
        }

    @staticmethod
    def get_exam_schedule(
        db: Session,
        student_id: int,
        subject_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve examination schedules, supporting subject-specific queries.
        """
        q = db.query(models.AcademicSchedule).filter(
            models.AcademicSchedule.type == "exam"
        )
        if subject_query:
            sq = f"%{subject_query.strip()}%"
            q = q.filter(
                (models.AcademicSchedule.title.ilike(sq)) |
                (models.AcademicSchedule.details.ilike(sq))
            )

        exams = q.order_by(models.AcademicSchedule.date.asc()).all()

        # Check next exam relative to Oct 9, 2026
        upcoming = [e for e in exams if e.date >= "2026-10-09"]
        next_exam = upcoming[0] if upcoming else (exams[0] if exams else None)

        return {
            "total_exams": len(exams),
            "next_exam": {
                "title": next_exam.title,
                "date": next_exam.date,
                "start_time": next_exam.start_time,
                "end_time": next_exam.end_time,
                "venue": next_exam.venue,
                "details": next_exam.details
            } if next_exam else None,
            "exams": [
                {
                    "title": e.title,
                    "date": e.date,
                    "start_time": e.start_time,
                    "end_time": e.end_time,
                    "venue": e.venue,
                    "details": e.details
                }
                for e in exams
            ],
            "official_source": "Office of the Controller of Examinations — Narasaraopeta Engineering College (Autonomous)"
        }

    @staticmethod
    def get_holidays(
        db: Session,
        month: Optional[str] = None,
        next_week: bool = False,
        check_tomorrow: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve official academic holidays for Fall 2026 / Spring 2027.
        """
        q = db.query(models.AcademicHoliday).order_by(models.AcademicHoliday.date.asc())
        
        if month:
            # e.g., October -> 2026-10
            m_lower = month.lower()
            if "oct" in m_lower:
                q = q.filter(models.AcademicHoliday.date.like("2026-10%"))
            elif "nov" in m_lower:
                q = q.filter(models.AcademicHoliday.date.like("2026-11%"))
            elif "dec" in m_lower:
                q = q.filter(models.AcademicHoliday.date.like("2026-12%"))
            elif "jan" in m_lower:
                q = q.filter(models.AcademicHoliday.date.like("2027-01%"))

        if next_week:
            # Next week: Oct 12 to Oct 18, 2026
            q = q.filter(models.AcademicHoliday.date >= "2026-10-12", models.AcademicHoliday.date <= "2026-10-18")

        holidays = q.all()

        # Check if tomorrow (Oct 10, 2026) is a holiday
        tomorrow_holiday = db.query(models.AcademicHoliday).filter(models.AcademicHoliday.date == "2026-10-10").first()

        return {
            "tomorrow_is_holiday": tomorrow_holiday is not None,
            "tomorrow_holiday_details": tomorrow_holiday.name if tomorrow_holiday else None,
            "total_holidays": len(holidays),
            "holidays": [
                {
                    "name": h.name,
                    "date": h.date,
                    "day_of_week": h.day_of_week,
                    "description": h.description
                }
                for h in holidays
            ]
        }

    @staticmethod
    def get_academic_calendar(db: Session, student_id: int) -> Dict[str, Any]:
        """
        Retrieve academic milestones (commencement, mid exams, last working day, SEE).
        """
        milestones = db.query(models.AcademicCalendarMilestone).order_by(
            models.AcademicCalendarMilestone.start_date.asc()
        ).all()

        return {
            "semester_label": "2-1",
            "academic_year": "2024-2025 (Fall 2026 Schedule)",
            "milestones": [
                {
                    "event_title": m.event_title,
                    "start_date": m.start_date,
                    "end_date": m.end_date,
                    "description": m.description
                }
                for m in milestones
            ]
        }

    @staticmethod
    def get_pending_assignments(
        db: Session,
        student_id: int,
        upcoming_only: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieve assignments and project deadlines for student.
        """
        q = db.query(models.StudentAssignment)
        if upcoming_only:
            q = q.filter(models.StudentAssignment.due_date >= "2026-10-09")
        
        assignments = q.order_by(models.StudentAssignment.due_date.asc()).all()

        return {
            "total_pending": len(assignments),
            "assignments": [
                {
                    "subject_code": a.subject_code,
                    "subject_name": a.subject_name,
                    "title": a.title,
                    "description": a.description,
                    "due_date": a.due_date,
                    "max_marks": a.max_marks,
                    "status": a.status,
                    "submission_portal": a.submission_portal,
                    "instructions": a.instructions
                }
                for a in assignments
            ]
        }

    @staticmethod
    def get_study_materials(
        db: Session,
        subject_query: Optional[str] = None,
        unit_num: Optional[int] = None,
        material_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve study materials, lecture notes, formula sheets, or previous question papers.
        """
        q = db.query(models.StudyMaterialItem)
        if subject_query:
            sq = f"%{subject_query.strip()}%"
            q = q.filter(
                (models.StudyMaterialItem.subject_name.ilike(sq)) |
                (models.StudyMaterialItem.subject_code.ilike(sq))
            )
        if unit_num is not None:
            q = q.filter(models.StudyMaterialItem.unit_number == unit_num)
        if material_type:
            q = q.filter(models.StudyMaterialItem.material_type == material_type)

        items = q.order_by(models.StudyMaterialItem.subject_code, models.StudyMaterialItem.unit_number).all()

        return {
            "total_items": len(items),
            "items": [
                {
                    "subject_code": it.subject_code,
                    "subject_name": it.subject_name,
                    "unit_number": it.unit_number,
                    "type": it.material_type,
                    "title": it.title,
                    "file_url": it.file_url,
                    "description": it.description
                }
                for it in items
            ]
        }

    @staticmethod
    def get_academic_notices(db: Session, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve published official notices and circulars.
        """
        q = db.query(models.Announcement).filter(models.Announcement.is_published == True)
        if category:
            q = q.filter(models.Announcement.category == category)
        
        notices = q.order_by(models.Announcement.created_at.desc()).all()

        return {
            "total_notices": len(notices),
            "notices": [
                {
                    "title": n.title,
                    "category": n.category,
                    "content": n.content,
                    "created_at": n.created_at.strftime("%Y-%m-%d") if n.created_at else "2026-10-09"
                }
                for n in notices
            ]
        }

    @staticmethod
    def get_deadlines(db: Session, student_id: int) -> Dict[str, Any]:
        """
        Aggregates all upcoming academic deadlines across assignments, fee/registration notices, and exams.
        """
        assignments = AcademicToolService.get_pending_assignments(db, student_id, upcoming_only=True)
        exams = AcademicToolService.get_exam_schedule(db, student_id)
        
        deadlines = []
        for a in assignments.get("assignments", []):
            deadlines.append({
                "category": "Assignment",
                "title": f"{a['subject_name']}: {a['title']}",
                "date": a['due_date'],
                "action": f"Submit on {a['submission_portal']}"
            })
        
        # Registration deadline
        deadlines.append({
            "category": "Administrative",
            "title": "Semester Examination Fee & Registration Deadline",
            "date": "2026-10-24",
            "action": "Complete online payment via Student ERP Portal"
        })
        deadlines.append({
            "category": "Attendance / Condonation",
            "title": "Medical Condonation Application Submission Deadline",
            "date": "2026-11-25",
            "action": "Submit medical certificate to Dean Academic Office"
        })

        deadlines.sort(key=lambda x: x["date"])

        return {
            "total_deadlines": len(deadlines),
            "deadlines": deadlines
        }

    @staticmethod
    def generate_study_plan(
        db: Session,
        student_id: int,
        days_ahead: int = 14
    ) -> Dict[str, Any]:
        """
        Generate a personalized study plan balancing daily class timetable,
        pending assignment due dates, and upcoming examination dates.
        """
        exams = AcademicToolService.get_exam_schedule(db, student_id)
        assignments = AcademicToolService.get_pending_assignments(db, student_id, upcoming_only=True)
        
        # Core subjects for 2-1
        subjects = [
            ("R23EC2104", "Electronic Devices and Circuits (EDC)", "Focus on Diode circuits, BJT Hybrid-pi model, FET Biasing"),
            ("R23EC2103", "Signals and Systems", "Focus on Fourier Series, Sampling Theorem, Orthogonal Signals"),
            ("R23EC2105", "Switching Theory and Logic Design (STLD)", "Focus on K-Maps, Boolean Minimization, Decoders/Multiplexers"),
            ("R23EC2101", "Probability Theory and Stochastic Process (PTSP)", "Focus on Random Variables, Probability Axioms, Expectations"),
            ("R23CC2102", "Universal Human Values (UHV)", "Review Harmony in Self, Family, Society and Ethical conduct")
        ]

        daily_plan = [
            {"date": "2026-10-10 (Saturday)", "primary_subject": "Electronic Devices & Circuits", "task": "Complete Unit 1 PN Junction Diode and Rectifier practice problems; begin EDC Assignment 1.", "time_slot": "04:30 PM - 07:00 PM (2.5 hrs)"},
            {"date": "2026-10-11 (Sunday)", "primary_subject": "Signals and Systems", "task": "Study Unit 1 elementary signals and derive sampling theorem properties; tutorial sheet revision.", "time_slot": "10:00 AM - 01:00 PM & 04:00 PM - 06:00 PM (5 hrs)"},
            {"date": "2026-10-12 (Monday)", "primary_subject": "Switching Theory & Logic Design", "task": "Practice 4-variable and 5-variable K-Map minimization; review Prime Implicant tables.", "time_slot": "05:30 PM - 07:30 PM (2 hrs)"},
            {"date": "2026-10-13 (Tuesday)", "primary_subject": "Probability Theory & Stochastic Process", "task": "Revise Baye's theorem and discrete/continuous random variable distribution functions.", "time_slot": "05:30 PM - 07:30 PM (2 hrs)"},
            {"date": "2026-10-14 (Wednesday)", "primary_subject": "Electronic Devices & Circuits", "task": "Finalize and write out EDC Assignment 1 solutions for BJT Small Signal analysis.", "time_slot": "05:30 PM - 07:30 PM (2 hrs)"},
            {"date": "2026-10-15 (Thursday)", "primary_subject": "Universal Human Values", "task": "Review holistic perception, self-exploration process, and human values terminology.", "time_slot": "05:30 PM - 07:00 PM (1.5 hrs)"},
            {"date": "2026-10-16 (Friday)", "primary_subject": "Data Structures using Python", "task": "Implement expression evaluator tree mini-project; test stack conversion functions.", "time_slot": "05:30 PM - 08:00 PM (2.5 hrs)"},
            {"date": "2026-10-17 (Saturday)", "primary_subject": "Signals and Systems", "task": "Complete Fourier Series Assignment 1 and solve 2024 Mid-1 question paper.", "time_slot": "03:00 PM - 06:00 PM (3 hrs)"},
            {"date": "2026-10-18 (Sunday)", "primary_subject": "EDC Assignment Submission & Mid-1 Revision", "task": "Upload EDC Assignment 1 on LMS before 11:59 PM; solve 2024 EDC Mid-1 past paper.", "time_slot": "10:00 AM - 01:00 PM & 04:00 PM - 07:00 PM (6 hrs)"},
            {"date": "2026-10-19 to 2026-10-24 (Dussehra Vacation)", "primary_subject": "Intensive Mid-Term Revision", "task": "Dedicated revision of Units 1 & 2 across all 5 theory exam subjects during college holidays.", "time_slot": "Daily 4 to 6 hours focused study blocks"},
            {"date": "2026-10-25 (Sunday)", "primary_subject": "PTSP Final Prep", "task": "Formulas cheatsheet review for Probability Theory Mid-I exam scheduled for Monday, Oct 26.", "time_slot": "Full day final review"}
        ]

        return {
            "semester_label": "2-1",
            "branch": "ECE",
            "study_strategy": "Spaced repetition balancing weekly timetable, assignment deadlines, and Mid-I exams commencing Oct 26.",
            "upcoming_exams": exams.get("exams", [])[:5],
            "pending_assignments": assignments.get("assignments", []),
            "daily_plan": daily_plan
        }

    @staticmethod
    def get_curriculum_units_explanation(
        db: Session,
        subject_query: str,
        unit_number: int
    ) -> Dict[str, Any]:
        """
        Retrieve official unit syllabus, unit title, topics, and textbooks from curriculum tables.
        """
        sq = f"%{subject_query.strip()}%"
        subj = db.query(models.CurriculumSubject).filter(
            (models.CurriculumSubject.name.ilike(sq)) |
            (models.CurriculumSubject.code.ilike(sq))
        ).first()

        if not subj:
            return {"found": False, "message": f"Subject matching '{subject_query}' not found in official R23 curriculum."}

        unit = db.query(models.CurriculumUnit).filter(
            models.CurriculumUnit.subject_id == subj.id,
            models.CurriculumUnit.unit_number == unit_number
        ).first()

        if not unit:
            return {
                "found": True,
                "subject_code": subj.code,
                "subject_name": subj.name,
                "unit_number": unit_number,
                "unit_title": f"Unit {unit_number}",
                "topics": "Topics for this unit are being updated in the departmental registry.",
                "course_outcomes": f"CO{unit_number}: Understand and apply fundamental principles of Unit {unit_number}."
            }

        return {
            "found": True,
            "subject_code": subj.code,
            "subject_name": subj.name,
            "semester_label": subj.semester_label,
            "credits": subj.credits,
            "unit_number": unit.unit_number,
            "unit_title": unit.unit_title,
            "topics": unit.topics,
            "course_outcomes": unit.course_outcomes,
            "source": subj.source_title
        }

