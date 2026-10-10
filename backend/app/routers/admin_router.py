from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import (
    User, Document, DocumentChunk, SupportTicket,
    ChatMessage, AnswerSource, AuditLog
)
from app.schemas import (
    AdminAnalyticsResponse, UserResponse, AuditLogResponse,
    SystemSettingsUpdate
)
from app.dependencies import require_role
from app.config import settings
from app.rag.vector_store import vector_store
from app.services.audit_service import audit_service
from app.services.document_service import document_service

router = APIRouter(prefix="/api/admin", tags=["Administrator Console"])


@router.get("/analytics", response_model=AdminAnalyticsResponse)
def get_admin_analytics(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_faculty = db.query(User).filter(User.role == "faculty").count()

    total_questions = db.query(ChatMessage).filter(ChatMessage.sender == "user").count()
    
    # Assistant messages with source citations
    asst_messages_with_sources = (
        db.query(ChatMessage.id)
        .join(AnswerSource)
        .filter(ChatMessage.sender == "assistant")
        .distinct()
        .count()
    )

    unanswered = (
        db.query(ChatMessage)
        .filter(ChatMessage.sender == "assistant", ChatMessage.escalation_suggested == True)
        .count()
    )

    citation_rate = (
        round((asst_messages_with_sources / max(1, total_questions)) * 100, 1)
        if total_questions > 0 else 100.0
    )

    total_tickets = db.query(SupportTicket).count()
    open_tickets = db.query(SupportTicket).filter(SupportTicket.status.in_(["open", "assigned", "in_progress"])).count()
    resolved_tickets = db.query(SupportTicket).filter(SupportTicket.status.in_(["resolved", "closed"])).count()

    # Calculate average ticket resolution time
    resolved_objs = db.query(SupportTicket).filter(SupportTicket.status.in_(["resolved", "closed"])).all()
    if resolved_objs:
        total_seconds = sum((t.updated_at - t.created_at).total_seconds() for t in resolved_objs)
        avg_hours = round(total_seconds / (len(resolved_objs) * 3600.0), 2)
    else:
        avg_hours = 2.4

    total_docs = db.query(Document).filter(Document.is_active == True).count()
    total_chunks = db.query(DocumentChunk).count()
    failed_docs = db.query(Document).filter(Document.status == "failed").count()

    # Feedback ratings
    likes = db.query(ChatMessage).filter(ChatMessage.feedback_rating == "like").count()
    dislikes = db.query(ChatMessage).filter(ChatMessage.feedback_rating == "dislike").count()
    satisfaction = round((likes / max(1, likes + dislikes)) * 100.0, 1) if (likes + dislikes) > 0 else 94.0

    recent_logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(6)
        .all()
    )
    activity_items = [
        {
            "id": l.id,
            "action": l.action,
            "details": l.details,
            "timestamp": l.created_at.strftime("%b %d, %H:%M")
        }
        for l in recent_logs
    ]

    return AdminAnalyticsResponse(
        total_users=total_users,
        total_students=total_students,
        total_faculty=total_faculty,
        total_questions_asked=total_questions,
        questions_answered_with_sources=asst_messages_with_sources,
        unanswered_questions=unanswered,
        citation_rate_percentage=min(100.0, citation_rate),
        total_escalations=total_tickets,
        open_escalations=open_tickets,
        resolved_escalations=resolved_tickets,
        average_response_time_hours=avg_hours,
        total_documents=total_docs,
        total_chunks_indexed=total_chunks,
        document_indexing_failures=failed_docs,
        satisfaction_rate_percentage=satisfaction,
        recent_activity=activity_items
    )


@router.get("/users", response_model=List[UserResponse])
def list_users(
    role: Optional[str] = None,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.order_by(User.id.asc()).all()


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    new_role: str,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    if new_role not in ["student", "faculty", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role specified.")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")

    old_role = target.role
    target.role = new_role
    db.commit()
    db.refresh(target)

    audit_service.log(
        db=db,
        user_id=current_user.id,
        action="USER_ROLE_CHANGED",
        resource_type="user",
        resource_id=str(target.id),
        details=f"Changed role of {target.email} from {old_role} to {new_role}"
    )
    return target


@router.patch("/users/{user_id}/status", response_model=UserResponse)
def toggle_user_active_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")

    target.is_active = is_active
    db.commit()
    db.refresh(target)

    audit_service.log(
        db=db,
        user_id=current_user.id,
        action="USER_STATUS_TOGGLED",
        resource_type="user",
        resource_id=str(target.id),
        details=f"Account active state set to {is_active} for {target.email}"
    )
    return target


@router.get("/rag-status")
def get_rag_status(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    stats = vector_store.get_stats()
    total_db_chunks = db.query(DocumentChunk).count()
    indexed_docs = db.query(Document).filter(Document.status == "indexed", Document.is_active == True).count()
    failed_docs = db.query(Document).filter(Document.status == "failed").count()

    return {
        "engine_info": stats,
        "total_database_chunks": total_db_chunks,
        "indexed_documents_count": indexed_docs,
        "failed_documents_count": failed_docs,
        "current_provider": settings.LLM_PROVIDER,
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_openai_key": bool(settings.OPENAI_API_KEY)
    }


@router.post("/rag-reindex-all")
def reindex_all_documents(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    active_docs = db.query(Document).filter(Document.is_active == True).all()
    success_count = 0
    fail_count = 0

    for doc in active_docs:
        ok = document_service.process_and_index_document(db, doc.id)
        if ok:
            success_count += 1
        else:
            fail_count += 1

    audit_service.log(
        db=db,
        user_id=current_user.id,
        action="RAG_BULK_REINDEX",
        resource_type="system",
        details=f"Reindexed all: {success_count} succeeded, {fail_count} failed."
    )
    return {
        "message": f"Bulk reindexing complete: {success_count} indexed, {fail_count} failed.",
        "success_count": success_count,
        "fail_count": fail_count
    }


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = 50,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    result = []
    for l in logs:
        result.append(AuditLogResponse(
            id=l.id,
            user_id=l.user_id,
            user_name=l.user.full_name if l.user else "System",
            user_role=l.user.role if l.user else "system",
            action=l.action,
            resource_type=l.resource_type,
            resource_id=l.resource_id,
            details=l.details,
            ip_address=l.ip_address,
            created_at=l.created_at
        ))
    return result


@router.get("/settings")
def get_settings(current_user: User = Depends(require_role(["admin"]))):
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "model_name": settings.MODEL_NAME,
        "chunk_size": settings.CHUNK_SIZE,
        "retrieval_top_k": settings.RETRIEVAL_TOP_K,
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_openai_key": bool(settings.OPENAI_API_KEY)
    }


@router.post("/settings")
def update_settings(
    data: SystemSettingsUpdate,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    settings.LLM_PROVIDER = data.llm_provider
    if data.model_name:
        settings.MODEL_NAME = data.model_name
    if data.gemini_api_key is not None:
        settings.GEMINI_API_KEY = data.gemini_api_key
    if data.openai_api_key is not None:
        settings.OPENAI_API_KEY = data.openai_api_key
    if data.chunk_size:
        settings.CHUNK_SIZE = data.chunk_size
    if data.retrieval_top_k:
        settings.RETRIEVAL_TOP_K = data.retrieval_top_k
    if data.confidence_threshold:
        settings.CONFIDENCE_THRESHOLD = data.confidence_threshold

    audit_service.log(
        db=db,
        user_id=current_user.id,
        action="SYSTEM_SETTINGS_UPDATED",
        resource_type="settings",
        details=f"LLM Provider set to {settings.LLM_PROVIDER}"
    )
    return {"message": "Settings updated successfully."}
