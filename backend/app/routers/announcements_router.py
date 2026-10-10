from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Announcement, User
from app.schemas import AnnouncementCreate, AnnouncementResponse
from app.dependencies import get_current_user, require_role
from app.services.notification_service import notification_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/api/announcements", tags=["Announcements"])


@router.get("", response_model=List[AnnouncementResponse])
def get_announcements(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Announcement).filter(Announcement.is_published == True)
    if category:
        query = query.filter(Announcement.category == category)
    announcements = query.order_by(Announcement.created_at.desc()).all()

    result = []
    for a in announcements:
        result.append(AnnouncementResponse(
            id=a.id,
            author_id=a.author_id,
            author_name=a.author.full_name if a.author else "Dean Office",
            title=a.title,
            content=a.content,
            category=a.category,
            department_id=a.department_id,
            department_name=a.department.name if a.department else None,
            is_published=a.is_published,
            created_at=a.created_at
        ))
    return result


@router.post("", response_model=AnnouncementResponse)
def create_announcement(
    data: AnnouncementCreate,
    current_user: User = Depends(require_role(["faculty", "admin"])),
    db: Session = Depends(get_db)
):
    announcement = Announcement(
        author_id=current_user.id,
        title=data.title,
        content=data.content,
        category=data.category,
        department_id=data.department_id,
        is_published=data.is_published
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)

    # Disseminate in-app notification to all active students
    students = db.query(User).filter(User.role == "student", User.is_active == True).all()
    for st in students:
        notification_service.create_notification(
            db=db,
            user_id=st.id,
            title=f"New Announcement: {data.title}",
            message=data.content[:140] + ("..." if len(data.content) > 140 else ""),
            notif_type="announcement",
            link_url="/student/dashboard"
        )

    audit_service.log(
        db=db,
        user_id=current_user.id,
        action="ANNOUNCEMENT_PUBLISHED",
        resource_type="announcement",
        resource_id=str(announcement.id),
        details=f"Title: {data.title}"
    )

    return AnnouncementResponse(
        id=announcement.id,
        author_id=announcement.author_id,
        author_name=current_user.full_name,
        title=announcement.title,
        content=announcement.content,
        category=announcement.category,
        department_id=announcement.department_id,
        department_name=announcement.department.name if announcement.department else None,
        is_published=announcement.is_published,
        created_at=announcement.created_at
    )


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    current_user: User = Depends(require_role(["faculty", "admin"])),
    db: Session = Depends(get_db)
):
    a = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Announcement not found.")

    if current_user.role == "faculty" and a.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this announcement.")

    db.delete(a)
    db.commit()
    return {"message": "Announcement deleted successfully."}
