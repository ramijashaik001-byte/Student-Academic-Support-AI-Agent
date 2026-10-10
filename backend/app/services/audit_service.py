from typing import Optional
from sqlalchemy.orm import Session
from app.models import AuditLog


class AuditService:
    @staticmethod
    def log(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: str = "127.0.0.1"
    ) -> AuditLog:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            details=details,
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit


audit_service = AuditService()
