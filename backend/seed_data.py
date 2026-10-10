from pathlib import Path
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import (
    User, StudentProfile, FacultyProfile, Department, Course,
    Subject, CourseEnrollment, Document, AcademicSchedule,
    Announcement, SupportTicket, TicketMessage, Notification
)
from app.auth import get_password_hash
from app.services.document_service import document_service
from app.config import settings

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        if db.query(User).count() > 0:
            print("Database already contains data. Skipping initial entity seed.")
            return

        print("--- Seeding Departments ---")
        cse_dept = Department(code="CSE", name="Computer Science & Engineering", head_of_department="Prof. Rajesh Sharma")
        it_dept = Department(code="IT", name="Information Technology", head_of_department="Dr. K. S. Verma")
        aids_dept = Department(code="AIDS", name="Artificial Intelligence & Data Science", head_of_department="Dr. Anita Rao")
        db.add_all([cse_dept, it_dept, aids_dept])
        db.commit()
        db.refresh(cse_dept)
        db.refresh(it_dept)
        db.refresh(aids_dept)

        print("--- Seeding Users & Profiles ---")
        # 1. Admin
        admin = User(
            email="admin@campus.edu",
            hashed_password=get_password_hash("Admin@123"),
            full_name="Dr. Campus Administrator",
            role="admin",
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
            is_active=True
        )
        db.add(admin)

        # 2. Faculty
        prof_sharma = User(
            email="prof.sharma@campus.edu",
            hashed_password=get_password_hash("Faculty@123"),
            full_name="Prof. Rajesh Sharma",
            role="faculty",
            avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
            is_active=True
        )
        dr_anita = User(
            email="dr.anita@campus.edu",
            hashed_password=get_password_hash("Faculty@123"),
            full_name="Dr. Anita Rao",
            role="faculty",
            avatar_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150",
            is_active=True
        )
        db.add_all([prof_sharma, dr_anita])
        db.commit()
        db.refresh(admin)
        db.refresh(prof_sharma)
        db.refresh(dr_anita)

        sharma_prof = FacultyProfile(
            user_id=prof_sharma.id,
            employee_id="FAC-CSE-001",
            department_id=cse_dept.id,
            designation="Professor & HOD",
            office_location="Block B, Room 301",
            office_hours="Mon-Thu 2:00 PM - 4:00 PM"
        )
        anita_prof = FacultyProfile(
            user_id=dr_anita.id,
            employee_id="FAC-AIDS-002",
            department_id=aids_dept.id,
            designation="Associate Professor",
            office_location="Block C, Room 204",
            office_hours="Tue-Fri 3:00 PM - 5:00 PM"
        )
        db.add_all([sharma_prof, anita_prof])

        # 3. Students
        student_ramija = User(
            email="ramija.student@campus.edu",
            hashed_password=get_password_hash("Student@123"),
            full_name="Ramija Shaik",
            role="student",
            avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150",
            is_active=True
        )
        student_rahul = User(
            email="rahul.student@campus.edu",
            hashed_password=get_password_hash("Student@123"),
            full_name="Rahul Verma",
            role="student",
            avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150",
            is_active=True
        )
        db.add_all([student_ramija, student_rahul])
        db.commit()
        db.refresh(student_ramija)
        db.refresh(student_rahul)

        ramija_profile = StudentProfile(
            user_id=student_ramija.id,
            roll_number="2026-CS-101",
            department_id=cse_dept.id,
            current_semester=6,
            academic_year="2025-2026",
            cgpa=8.85
        )
        rahul_profile = StudentProfile(
            user_id=student_rahul.id,
            roll_number="2026-CS-102",
            department_id=cse_dept.id,
            current_semester=6,
            academic_year="2025-2026",
            cgpa=7.92
        )
        db.add_all([ramija_profile, rahul_profile])
        db.commit()
        db.refresh(ramija_profile)
        db.refresh(rahul_profile)

        print("--- Seeding Courses & Subjects ---")
        c1 = Course(department_id=cse_dept.id, code="CS301", name="Operating Systems", semester=6, credits=4, syllabus_summary="Processes, CPU Scheduling, Synchronization, Memory, Deadlocks")
        c2 = Course(department_id=cse_dept.id, code="CS302", name="Database Management Systems", semester=6, credits=4, syllabus_summary="Relational Model, SQL, Normalization, Transactions, B-Trees")
        c3 = Course(department_id=cse_dept.id, code="CS303", name="Computer Networks", semester=6, credits=3, syllabus_summary="OSI Model, TCP/IP, Routing Protocols, Congestion Control")
        c4 = Course(department_id=aids_dept.id, code="CS304", name="Artificial Intelligence & ML", semester=6, credits=4, syllabus_summary="Search Algorithms, Supervised Learning, Deep Neural Networks")
        c5 = Course(department_id=cse_dept.id, code="CS305", name="Cloud Computing & DevOps", semester=6, credits=3, syllabus_summary="Microservices, Docker, Kubernetes, CI/CD, AWS Architecture")
        db.add_all([c1, c2, c3, c4, c5])
        db.commit()
        db.refresh(c1)
        db.refresh(c2)
        db.refresh(c3)
        db.refresh(c4)
        db.refresh(c5)

        s1 = Subject(course_id=c1.id, faculty_id=prof_sharma.id, code="CS301-TH", name="Operating Systems Theory", description="Core theoretical systems programming")
        s2 = Subject(course_id=c2.id, faculty_id=dr_anita.id, code="CS302-TH", name="DBMS Theory & Labs", description="Relational and NoSQL distributed databases")
        db.add_all([s1, s2])

        # Enroll students
        for course_obj in [c1, c2, c3, c4, c5]:
            db.add(CourseEnrollment(student_id=ramija_profile.id, course_id=course_obj.id))
            db.add(CourseEnrollment(student_id=rahul_profile.id, course_id=course_obj.id))
        db.commit()

        print("--- Seeding Academic Schedules ---")
        schedules = [
            AcademicSchedule(title="CS301 Operating Systems Mid-Term", type="exam", course_id=c1.id, date="2026-10-26", start_time="10:00 AM", end_time="12:00 PM", venue="Hall A, Block 2", details="Mid-Semester examination on Units 1 and 2."),
            AcademicSchedule(title="CS302 DBMS Mid-Term", type="exam", course_id=c2.id, date="2026-10-28", start_time="10:00 AM", end_time="12:00 PM", venue="Hall A, Block 2", details="Mid-Semester examination covering SQL and Normalization."),
            AcademicSchedule(title="CS303 Computer Networks Mid-Term", type="exam", course_id=c3.id, date="2026-10-30", start_time="10:00 AM", end_time="12:00 PM", venue="Hall B, Block 2", details="TCP/IP protocols, Subnetting, and Routing."),
            AcademicSchedule(title="CS301 CPU Simulator Assignment", type="deadline", course_id=c1.id, date="2026-10-20", start_time="11:59 PM", end_time="11:59 PM", venue="LMS Portal", details="Submit simulation script in Python or C++."),
            AcademicSchedule(title="CS302 SQL Window Functions Lab", type="deadline", course_id=c2.id, date="2026-10-25", start_time="11:59 PM", end_time="11:59 PM", venue="LMS Portal", details="Complete queries with execution plans."),
            AcademicSchedule(title="Operating Systems Lab Session", type="class", course_id=c1.id, date="2026-10-15", start_time="02:00 PM", end_time="04:00 PM", venue="Lab 304, CS Block", details="Linux thread synchronization lab."),
        ]
        db.add_all(schedules)
        db.commit()

        print("--- Seeding Announcements ---")
        a1 = Announcement(
            author_id=admin.id,
            title="Mid-Semester Examination Schedule Published - Fall 2026",
            content="The official mid-semester timetable has been released by the Controller of Examinations. Exams start on October 26, 2026. Hall tickets can be downloaded from the student portal starting October 22.",
            category="exam",
            department_id=None,
            is_published=True
        )
        a2 = Announcement(
            author_id=prof_sharma.id,
            title="Mandatory 75% Attendance Review & Medical Condonation",
            content="Students are reminded that 75% aggregate attendance is mandatory to appear for examinations. Those with attendance between 65% and 74% must submit medical documentation before the condonation deadline.",
            category="academic",
            department_id=cse_dept.id,
            is_published=True
        )
        a3 = Announcement(
            author_id=dr_anita.id,
            title="Extended Computer Lab Working Hours for Capstone Projects",
            content="Computer Laboratories 302 and 304 will remain open until 8:30 PM on weekdays to facilitate term project development and testing on the GPU clusters.",
            category="general",
            department_id=aids_dept.id,
            is_published=True
        )
        db.add_all([a1, a2, a3])
        db.commit()

        print("--- Ingesting & Indexing Sample Academic Documents ---")
        sample_files = [
            ("Academic Regulations and Attendance Policy 2026", "Academic_Regulations_and_Attendance_Policy_2026.pdf", "policy", cse_dept.id, None),
            ("Mid-Semester Examination Guidelines and Timetable", "Mid_Semester_Examination_Guidelines_and_Timetable.pdf", "exam_timetable", cse_dept.id, None),
            ("CS301 Operating Systems Syllabus and Deadlines", "CS301_Operating_Systems_Syllabus_and_Deadlines.docx", "syllabus", cse_dept.id, c1.id),
            ("CS302 Database Management Systems Lab Guide", "CS302_Database_Management_Systems_Notes_and_Assignments.docx", "syllabus", cse_dept.id, c2.id),
            ("Lab Safety and Project Submission Guidelines", "Lab_Safety_and_Project_Submission_Guidelines.txt", "policy", cse_dept.id, None),
            ("Scholarship and Fee Structure Bylaws", "Scholarship_and_Fee_Structure_Bylaws.txt", "policy", None, None),
            ("Academic Calendar Fall 2026", "Academic_Calendar_Fall_2026.csv", "exam_timetable", None, None),
        ]

        for title, fname, category, dept_id, crs_id in sample_files:
            file_path = settings.SAMPLE_DOCS_DIR / fname
            if file_path.exists():
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                
                doc = document_service.save_and_create_document(
                    db=db,
                    uploader=prof_sharma,
                    title=title,
                    file_name=fname,
                    file_bytes=file_bytes,
                    category=category,
                    department_id=dept_id,
                    course_id=crs_id,
                    academic_year="2025-2026",
                    access_level="all"
                )
                print(f"  -> Indexed: {title} (ID: {doc.id}, Status: {doc.status})")

        print("--- Seeding Support Tickets & Messages ---")
        ticket1 = SupportTicket(
            ticket_number="TICK-2026-0001",
            student_id=student_ramija.id,
            faculty_id=prof_sharma.id,
            department_id=cse_dept.id,
            course_id=c1.id,
            subject="Discrepancy in CS301 Practical Lab Attendance Record",
            description="Dear Prof. Sharma, my portal shows 71% attendance for the Tuesday lab session, but I was present on Sept 16 and had signed the physical register. Could you please verify the lab ledger?",
            priority="high",
            status="waiting_for_student"
        )
        db.add(ticket1)
        db.commit()
        db.refresh(ticket1)

        m1 = TicketMessage(
            ticket_id=ticket1.id,
            sender_id=student_ramija.id,
            message="Dear Prof. Sharma, my portal shows 71% attendance for the Tuesday lab session, but I was present on Sept 16 and had signed the physical register. Could you please verify the lab ledger?"
        )
        m2 = TicketMessage(
            ticket_id=ticket1.id,
            sender_id=prof_sharma.id,
            message="Hello Ramija, I inspected the physical lab register for Sept 16. The attendance entry was mistakenly marked absent during spreadsheet sync. I have updated the portal records to present. Your updated attendance is now 76%."
        )
        db.add_all([m1, m2])
        db.commit()

        print("--- Seeding In-App Notifications ---")
        n1 = Notification(
            user_id=student_ramija.id,
            title="Faculty Responded to Ticket TICK-2026-0001",
            message="Prof. Rajesh Sharma replied to your query regarding CS301 lab attendance.",
            type="ticket_update",
            link_url="/student/tickets",
            is_read=False
        )
        n2 = Notification(
            user_id=student_ramija.id,
            title="Mid-Semester Exam Schedule Released",
            message="The examination timetable for Fall 2026 has been published. Exams begin Oct 26.",
            type="exam_schedule",
            link_url="/student/schedules",
            is_read=False
        )
        n3 = Notification(
            user_id=prof_sharma.id,
            title="New Student Ticket Assigned",
            message="Ticket TICK-2026-0001 was submitted by Ramija Shaik regarding CS301.",
            type="ticket_update",
            link_url=f"/faculty/escalations/{ticket1.id}",
            is_read=True
        )
        db.add_all([n1, n2, n3])
        db.commit()

        print("[SUCCESS] Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error during database seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
