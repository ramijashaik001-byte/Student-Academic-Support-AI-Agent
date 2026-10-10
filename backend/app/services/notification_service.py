from typing import List
from sqlalchemy.orm import Session
from app.models import Notification


class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notif_type: str = "system",
        link_url: str = None
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notif_type,
            link_url=link_url,
            is_read=False
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def get_user_notifications(db: Session, user_id: int, limit: int = 50) -> List[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .count()
        )

    @staticmethod
    def mark_read(db: Session, notification_id: int, user_id: int) -> bool:
        notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
        if notif:
            notif.is_read = True
            db.commit()
            return True
        return False

    @staticmethod
    def mark_all_read(db: Session, user_id: int) -> int:
        count = db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).update({"is_read": True})
        db.commit()
        return count


notification_service = NotificationService()
