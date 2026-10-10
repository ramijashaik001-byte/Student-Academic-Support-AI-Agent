from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Department, Course, Subject, AcademicSchedule, Document
from app.schemas import DepartmentResponse, CourseResponse, SubjectResponse, AcademicScheduleResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/academic", tags=["Academic Entities & Schedules"])


@router.get("/departments", response_model=List[DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()


@router.get("/courses", response_model=List[CourseResponse])
def get_courses(department_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Course)
    if department_id:
        query = query.filter(Course.department_id == department_id)
    courses = query.all()

    result = []
    for c in courses:
        result.append(CourseResponse(
            id=c.id,
            department_id=c.department_id,
            code=c.code,
            name=c.name,
            semester=c.semester,
            credits=c.credits,
            syllabus_summary=c.syllabus_summary,
            department_name=c.department.name if c.department else None
        ))
    return result


@router.get("/subjects", response_model=List[SubjectResponse])
def get_subjects(course_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Subject)
    if course_id:
        query = query.filter(Subject.course_id == course_id)
    subjects = query.all()

    result = []
    for s in subjects:
        result.append(SubjectResponse(
            id=s.id,
            course_id=s.course_id,
            faculty_id=s.faculty_id,
            code=s.code,
            name=s.name,
            description=s.description,
            faculty_name=s.faculty.full_name if s.faculty else "Unassigned"
        ))
    return result


@router.get("/schedules", response_model=List[AcademicScheduleResponse])
def get_schedules(schedule_type: Optional[str] = None, course_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(AcademicSchedule)
    if schedule_type:
        query = query.filter(AcademicSchedule.type == schedule_type)
    if course_id:
        query = query.filter(AcademicSchedule.course_id == course_id)
    
    schedules = query.order_by(AcademicSchedule.date.asc()).all()
    result = []
    for s in schedules:
        result.append(AcademicScheduleResponse(
            id=s.id,
            title=s.title,
            type=s.type,
            course_id=s.course_id,
            course_code=s.course.code if s.course else None,
            date=s.date,
            start_time=s.start_time,
            end_time=s.end_time,
            venue=s.venue,
            details=s.details
        ))
    return result


@router.get("/exam-guidelines")
def get_exam_guidelines(db: Session = Depends(get_db)):
    # Fetch guidelines from verified exam policy documents
    exam_docs = db.query(Document).filter(
        Document.is_active == True,
        Document.category.in_(["exam_timetable", "policy"])
    ).all()

    guidelines = [
        {"title": "Hall Ticket Mandatory", "rule": "Students must produce physical or digital institutional hall tickets along with college ID card at the examination hall."},
        {"title": "Reporting Time", "rule": "Report to the assigned examination room at least 20 minutes prior to exam commencement. Entry strictly closes 15 minutes after start."},
        {"title": "Prohibited Electronic Devices", "rule": "Mobile phones, programmable calculators, smart watches, and unauthorized paper slips are strictly banned under the malpractice policy."},
        {"title": "Minimum Passing Standard", "rule": "40% aggregate in continuous internal assessments (CIA) and semester end examinations (SEE)."},
        {"title": "Condonation & Medical Policy", "rule": "Attendance between 65% and 74% requires medical certificate submission to Dean Academic before hall ticket issuance."}
    ]
    return {
        "guidelines": guidelines,
        "verified_document_sources": [d.title for d in exam_docs]
    }
