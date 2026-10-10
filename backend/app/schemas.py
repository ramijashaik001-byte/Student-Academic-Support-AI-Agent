from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------------- Auth & User ----------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "student"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    roll_number: Optional[str] = None
    department_id: Optional[int] = None
    current_semester: Optional[int] = 1


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class StudentProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    roll_number: str
    department_id: Optional[int]
    department_name: Optional[str] = None
    current_semester: int
    academic_year: str
    cgpa: float


class FacultyProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    employee_id: str
    department_id: Optional[int]
    department_name: Optional[str] = None
    designation: str
    office_location: str
    office_hours: str


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    student_profile: Optional[StudentProfileResponse] = None
    faculty_profile: Optional[FacultyProfileResponse] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ---------------- Academic Entities ----------------
class DepartmentBase(BaseModel):
    code: str
    name: str
    head_of_department: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class CourseBase(BaseModel):
    department_id: int
    code: str
    name: str
    semester: int = 1
    credits: int = 3
    syllabus_summary: Optional[str] = None


class CourseResponse(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    department_name: Optional[str] = None


class SubjectBase(BaseModel):
    course_id: int
    faculty_id: Optional[int] = None
    code: str
    name: str
    description: Optional[str] = None


class SubjectResponse(SubjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    faculty_name: Optional[str] = None


class AcademicScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    type: str  # exam, class, deadline, holiday, event
    course_id: Optional[int] = None
    course_code: Optional[str] = None
    date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    venue: Optional[str] = None
    details: Optional[str] = None


# ---------------- Documents & RAG ----------------
class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    file_name: str
    file_type: str
    file_size: int
    category: str
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    course_id: Optional[int] = None
    course_code: Optional[str] = None
    academic_year: str
    access_level: str
    status: str
    error_message: Optional[str] = None
    uploaded_by: int
    uploader_name: Optional[str] = None
    chunks_count: Optional[int] = 0
    version: int
    created_at: datetime
    updated_at: datetime


class AnswerSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    document_id: Optional[int]
    document_title: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    excerpt: str
    relevance_score: float


class ChatFeedbackRequest(BaseModel):
    rating: str  # "like", "dislike"
    comment: Optional[str] = None


# ---------------- Chat & Conversations ----------------
class ChatAskRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None
    course_id: Optional[int] = None


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    conversation_id: int
    sender: str
    content: str
    confidence_score: Optional[float] = None
    escalation_suggested: bool = False
    feedback_rating: Optional[str] = None
    feedback_comment: Optional[str] = None
    sources: List[AnswerSourceResponse] = []
    follow_up_suggestions: List[str] = []
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None
    message_count: int = 0


class ConversationDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []


# ---------------- Support Tickets & Escalation ----------------
class TicketCreate(BaseModel):
    subject: str = Field(..., min_length=3)
    description: str = Field(..., min_length=5)
    priority: str = "medium"  # low, medium, high, urgent
    department_id: Optional[int] = None
    course_id: Optional[int] = None
    conversation_id: Optional[int] = None


class TicketMessageCreate(BaseModel):
    message: str = Field(..., min_length=1)
    attachment_url: Optional[str] = None


class TicketMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_id: int
    sender_id: int
    sender_name: str
    sender_role: str
    message: str
    attachment_url: Optional[str] = None
    created_at: datetime


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_number: str
    student_id: int
    student_name: str
    student_roll: Optional[str] = None
    faculty_id: Optional[int] = None
    faculty_name: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    course_id: Optional[int] = None
    course_name: Optional[str] = None
    conversation_id: Optional[int] = None
    subject: str
    description: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
    messages_count: int = 0
    messages: Optional[List[TicketMessageResponse]] = []


class TicketStatusUpdate(BaseModel):
    status: str  # open, assigned, in_progress, waiting_for_student, resolved, closed


class TicketAssignUpdate(BaseModel):
    faculty_id: int


# ---------------- Notifications ----------------
class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    title: str
    message: str
    type: str
    link_url: Optional[str] = None
    is_read: bool
    created_at: datetime


# ---------------- Announcements ----------------
class AnnouncementCreate(BaseModel):
    title: str
    content: str
    category: str = "general"
    department_id: Optional[int] = None
    is_published: bool = True


class AnnouncementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    author_id: int
    author_name: str
    title: str
    content: str
    category: str
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    is_published: bool
    created_at: datetime


# ---------------- Admin & Analytics ----------------
class AdminAnalyticsResponse(BaseModel):
    total_users: int
    total_students: int
    total_faculty: int
    total_questions_asked: int
    questions_answered_with_sources: int
    unanswered_questions: int
    citation_rate_percentage: float
    total_escalations: int
    open_escalations: int
    resolved_escalations: int
    average_response_time_hours: float
    total_documents: int
    total_chunks_indexed: int
    document_indexing_failures: int
    satisfaction_rate_percentage: float
    recent_activity: List[dict] = []


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: Optional[int]
    user_name: Optional[str] = None
    user_role: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: str
    created_at: datetime


class SystemSettingsUpdate(BaseModel):
    llm_provider: str  # "gemini", "openai", "local_fallback"
    model_name: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    chunk_size: Optional[int] = 550
    retrieval_top_k: Optional[int] = 4
    confidence_threshold: Optional[float] = 0.40


class ClassTimetableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    semester_label: str
    branch: str
    section: str
    day_of_week: str
    period_number: int
    start_time: str
    end_time: str
    subject_code: str
    subject_name: str
    faculty_name: str
    room_number: str
    is_lab: bool
    is_cancelled: bool
    change_note: Optional[str] = None
    academic_year: str


class AcademicHolidayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    date: str
    day_of_week: str
    is_restricted: bool
    description: Optional[str] = None


class StudentAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: Optional[int] = None
    semester_label: str
    subject_code: str
    subject_name: str
    title: str
    description: Optional[str] = None
    due_date: str
    max_marks: float
    status: str
    submission_portal: str
    instructions: Optional[str] = None


class StudyMaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject_code: str
    subject_name: str
    unit_number: Optional[int] = None
    material_type: str
    title: str
    file_url: Optional[str] = None
    description: Optional[str] = None
    academic_year: str

