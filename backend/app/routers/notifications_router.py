from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import NotificationResponse
from app.dependencies import get_current_user
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/notifications", tags=["In-App Notifications"])


@router.get("", response_model=List[NotificationResponse])
def get_user_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return notification_service.get_user_notifications(db=db, user_id=current_user.id)


@router.get("/unread-count")
def get_unread_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = notification_service.get_unread_count(db=db, user_id=current_user.id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read")
def mark_notification_read(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    success = notification_service.mark_read(db=db, notification_id=notification_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"message": "Notification marked as read."}


@router.post("/read-all")
def mark_all_notifications_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_count = notification_service.mark_all_read(db=db, user_id=current_user.id)
    return {"message": f"{updated_count} notifications marked as read."}
