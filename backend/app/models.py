import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Index, Enum
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="student")  # "student", "faculty", "admin"
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    faculty_profile = relationship("FacultyProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    tickets_as_student = relationship("SupportTicket", foreign_keys="SupportTicket.student_id", back_populates="student")
    tickets_as_faculty = relationship("SupportTicket", foreign_keys="SupportTicket.faculty_id", back_populates="faculty")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    current_semester = Column(Integer, default=1)
    academic_year = Column(String(50), default="2025-2026")
    cgpa = Column(Float, default=8.5)

    user = relationship("User", back_populates="student_profile")
    department = relationship("Department")
    enrollments = relationship("CourseEnrollment", back_populates="student", cascade="all, delete-orphan")
    semester_records = relationship("StudentSemesterRecord", back_populates="student_profile", cascade="all, delete-orphan")
    attendance_records = relationship("StudentAttendanceRecord", back_populates="student_profile", cascade="all, delete-orphan")


class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    designation = Column(String(100), default="Assistant Professor")
    office_location = Column(String(100), default="Block B, Room 304")
    office_hours = Column(String(200), default="Mon-Thu 2:00 PM - 4:00 PM")

    user = relationship("User", back_populates="faculty_profile")
    department = relationship("Department")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # CSE, ECE, MECH, etc.
    name = Column(String(255), nullable=False)
    head_of_department = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    courses = relationship("Course", back_populates="department")
    documents = relationship("Document", back_populates="department")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)  # CS301, CS302, etc.
    name = Column(String(255), nullable=False)
    semester = Column(Integer, default=1)
    credits = Column(Integer, default=3)
    syllabus_summary = Column(Text, nullable=True)

    department = relationship("Department", back_populates="courses")
    subjects = relationship("Subject", back_populates="course", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="course")
    enrollments = relationship("CourseEnrollment", back_populates="course")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), index=True, nullable=False)
    description = Column(Text, nullable=True)

    course = relationship("Course", back_populates="subjects")
    faculty = relationship("User")


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("StudentProfile", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt, csv
    file_size = Column(Integer, default=0)
    category = Column(String(100), default="general")  # syllabus, exam_timetable, policy, assignment, lecture_notes, general
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    academic_year = Column(String(50), default="2025-2026")
    access_level = Column(String(50), default="all")  # all, student, faculty
    status = Column(String(50), default="uploaded")  # uploaded, processing, indexed, failed
    error_message = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    department = relationship("Department", back_populates="documents")
    course = relationship("Course", back_populates="documents")
    uploader = relationship("User")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    section_heading = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="chunks")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="Academic Inquiry")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(50), nullable=False)  # "user", "assistant"
    content = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    escalation_suggested = Column(Boolean, default=False)
    feedback_rating = Column(String(20), nullable=True)  # "like", "dislike"
    feedback_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
    sources = relationship("AnswerSource", back_populates="message", cascade="all, delete-orphan")


class AnswerSource(Base):
    __tablename__ = "answer_sources"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    document_title = Column(String(255), nullable=False)
    page_number = Column(Integer, nullable=True)
    section = Column(String(255), nullable=True)
    excerpt = Column(Text, nullable=False)
    relevance_score = Column(Float, default=1.0)

    message = relationship("ChatMessage", back_populates="sources")
    document = relationship("Document")


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)  # e.g., TICK-2026-001
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(50), default="medium")  # low, medium, high, urgent
    status = Column(String(50), default="open")  # open, assigned, in_progress, waiting_for_student, resolved, closed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    student = relationship("User", foreign_keys=[student_id], back_populates="tickets_as_student")
    faculty = relationship("User", foreign_keys=[faculty_id], back_populates="tickets_as_faculty")
    department = relationship("Department")
    course = relationship("Course")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    attachment_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ticket = relationship("SupportTicket", back_populates="messages")
    sender = relationship("User")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="system")  # ticket_update, announcement, course_material, exam_schedule, system
    link_url = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), default="general")  # urgent, academic, exam, general
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    author = relationship("User")
    department = relationship("Department")


class AcademicSchedule(Base):
    __tablename__ = "academic_schedules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # exam, class, deadline, holiday, event
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    date = Column(String(50), nullable=False)  # e.g., "2026-10-25"
    start_time = Column(String(50), nullable=True)  # "10:00 AM"
    end_time = Column(String(50), nullable=True)  # "01:00 PM"
    venue = Column(String(100), nullable=True)  # "Hall A, Science Block"
    details = Column(Text, nullable=True)

    course = relationship("Course")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)  # USER_LOGIN, DOCUMENT_UPLOAD, TICKET_CREATED, ROLE_CHANGED, etc.
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(100), default="127.0.0.1")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


class AcademicProfileConfig(Base):
    __tablename__ = "academic_profile_configs"

    id = Column(Integer, primary_key=True, index=True)
    degree = Column(String(50), default="B.Tech")
    admission_batch = Column(String(50), default="2023-2027")
    institution = Column(String(255), default="Narasaraopeta Engineering College")
    institution_code = Column(String(50), default="47")
    branch = Column(String(50), default="ECE")  # Configurable (ECE, CSE, etc.)
    regulation = Column(String(50), default="R23")
    duration_years = Column(Integer, default=4)
    total_semesters = Column(Integer, default=8)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class CurriculumSubject(Base):
    __tablename__ = "curriculum_subjects"

    id = Column(Integer, primary_key=True, index=True)
    regulation = Column(String(50), default="R23", index=True)
    branch = Column(String(50), default="ECE", index=True)
    academic_year = Column(String(50), default="2023-2024")
    semester_label = Column(String(20), index=True, nullable=False)  # 1-1, 1-2, 2-1, 2-2, 3-1, 3-2, 4-1, 4-2
    code = Column(String(50), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    credits = Column(Float, nullable=False, default=3.0)
    lecture_hours = Column(Integer, default=3)
    tutorial_hours = Column(Integer, default=0)
    practical_hours = Column(Integer, default=0)
    subject_type = Column(String(50), default="theory")  # theory, lab, skill, audit, project, internship
    category = Column(String(50), default="PC")  # BS, ES, HS, PC, PE, OE, SC, MC, PR
    syllabus_summary = Column(Text, nullable=True)
    verification_status = Column(String(50), default="Verified Official")
    source_title = Column(String(255), default="Official NEC Autonomous Syllabus")
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    units = relationship("CurriculumUnit", back_populates="subject", cascade="all, delete-orphan")


class CurriculumUnit(Base):
    __tablename__ = "curriculum_units"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("curriculum_subjects.id", ondelete="CASCADE"), nullable=False)
    unit_number = Column(Integer, nullable=False)  # 1 to 5
    unit_title = Column(String(255), nullable=False)
    topics = Column(Text, nullable=False)
    course_outcomes = Column(Text, nullable=True)

    subject = relationship("CurriculumSubject", back_populates="units")


class StudentSemesterRecord(Base):
    __tablename__ = "student_semester_records"

    id = Column(Integer, primary_key=True, index=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    academic_year = Column(String(50), nullable=False)
    semester_label = Column(String(20), nullable=False, index=True)  # 1-1, 1-2, etc.
    examination_session = Column(String(100), nullable=True)  # e.g., "Regular Dec 2023"
    result_date = Column(String(50), nullable=True)
    total_credits_registered = Column(Float, default=0.0)
    credits_earned = Column(Float, default=0.0)
    sgpa = Column(Float, nullable=True)
    cgpa = Column(Float, nullable=True)
    result_status = Column(String(50), default="PASSED")  # PASSED, PROMOTED_WITH_BACKLOGS, DETAINED
    is_verified = Column(Boolean, default=True)
    source_document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    import_audit_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student_profile = relationship("StudentProfile", back_populates="semester_records")
    subject_records = relationship("StudentSubjectRecord", back_populates="semester_record", cascade="all, delete-orphan")


class StudentSubjectRecord(Base):
    __tablename__ = "student_subject_records"

    id = Column(Integer, primary_key=True, index=True)
    semester_record_id = Column(Integer, ForeignKey("student_semester_records.id", ondelete="CASCADE"), nullable=False)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    subject_code = Column(String(50), nullable=False, index=True)
    subject_name = Column(String(255), nullable=False)
    credits = Column(Float, nullable=False, default=3.0)
    internal_marks = Column(Float, nullable=True)
    external_marks = Column(Float, nullable=True)
    total_marks = Column(Float, nullable=True)
    maximum_marks = Column(Float, default=100.0)
    grade = Column(String(10), nullable=True)  # O, A, B, C, D, E, F, Ab
    grade_points = Column(Integer, nullable=True)  # 10, 9, 8, 7, 6, 5, 0
    pass_fail_status = Column(String(20), default="PASS")  # PASS, FAIL, ABSENT
    is_backlog = Column(Boolean, default=False)
    cleared_at_attempt = Column(Integer, default=1)
    attempt_number = Column(Integer, default=1)
    exam_session = Column(String(100), nullable=True)
    result_date = Column(String(50), nullable=True)
    source_file = Column(String(255), nullable=True)

    semester_record = relationship("StudentSemesterRecord", back_populates="subject_records")
    student_profile = relationship("StudentProfile")


class StudentAttendanceRecord(Base):
    __tablename__ = "student_attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    semester_label = Column(String(20), nullable=False, index=True)
    subject_code = Column(String(50), nullable=False)
    subject_name = Column(String(255), nullable=False)
    classes_conducted = Column(Integer, nullable=False, default=0)
    classes_attended = Column(Integer, nullable=False, default=0)
    attendance_percentage = Column(Float, nullable=False, default=0.0)
    target_percentage = Column(Float, default=75.0)
    condonation_eligible = Column(Boolean, default=False)
    detention_risk = Column(Boolean, default=False)
    source_document = Column(String(255), default="Department ERP Attendance Register")
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

    student_profile = relationship("StudentProfile", back_populates="attendance_records")


class MarksheetImportRecord(Base):
    __tablename__ = "marksheet_import_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    semester_label = Column(String(20), nullable=False)
    academic_year = Column(String(50), default="2023-2024")
    total_subjects_parsed = Column(Integer, default=0)
    verified_subjects_count = Column(Integer, default=0)
    validation_warnings = Column(Text, nullable=True)
    status = Column(String(50), default="draft")  # draft, validated, confirmed, rejected
    raw_payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("User")


class ClassTimetableEntry(Base):
    __tablename__ = "class_timetable_entries"

    id = Column(Integer, primary_key=True, index=True)
    semester_label = Column(String(20), nullable=False, index=True)  # 2-1, 1-1, etc.
    branch = Column(String(50), default="ECE", index=True)
    section = Column(String(10), default="A")
    day_of_week = Column(String(20), nullable=False, index=True)  # Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
    period_number = Column(Integer, nullable=False)  # 1 to 7
    start_time = Column(String(20), nullable=False)  # "09:00 AM"
    end_time = Column(String(20), nullable=False)    # "10:00 AM"
    subject_code = Column(String(50), nullable=False, index=True)
    subject_name = Column(String(255), nullable=False)
    faculty_name = Column(String(255), nullable=False)
    room_number = Column(String(100), nullable=False)
    is_lab = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)
    change_note = Column(String(255), nullable=True)  # e.g., "Shifted to Room 208 for guest lecture"
    academic_year = Column(String(50), default="2024-2025")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AcademicHoliday(Base):
    __tablename__ = "academic_holidays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    date = Column(String(50), nullable=False, index=True)  # YYYY-MM-DD
    day_of_week = Column(String(20), nullable=False)
    is_restricted = Column(Boolean, default=False)
    description = Column(Text, nullable=True)


class AcademicCalendarMilestone(Base):
    __tablename__ = "academic_calendar_milestones"

    id = Column(Integer, primary_key=True, index=True)
    event_title = Column(String(255), nullable=False)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=True)
    semester_label = Column(String(20), default="2-1")
    academic_year = Column(String(50), default="2024-2025")
    description = Column(Text, nullable=True)


class StudentAssignment(Base):
    __tablename__ = "student_assignments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    semester_label = Column(String(20), default="2-1")
    subject_code = Column(String(50), nullable=False, index=True)
    subject_name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(String(50), nullable=False, index=True)  # YYYY-MM-DD or datetime string
    max_marks = Column(Float, default=10.0)
    status = Column(String(50), default="pending")  # pending, submitted, graded
    submission_portal = Column(String(255), default="College LMS Portal")
    instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class StudyMaterialItem(Base):
    __tablename__ = "study_materials"

    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String(50), nullable=False, index=True)
    subject_name = Column(String(255), nullable=False)
    unit_number = Column(Integer, nullable=True)  # 1 to 5, or None for general/papers
    material_type = Column(String(50), default="lecture_notes")  # lecture_notes, question_paper, formula_sheet, lab_manual
    title = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    academic_year = Column(String(50), default="2024-2025")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


