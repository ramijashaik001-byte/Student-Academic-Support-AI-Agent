from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SupportTicket, TicketMessage, User
from app.schemas import (
    TicketCreate, TicketResponse, TicketMessageCreate,
    TicketMessageResponse, TicketStatusUpdate, TicketAssignUpdate
)
from app.dependencies import get_current_user, require_role
from app.services.ticket_service import ticket_service

router = APIRouter(prefix="/api/tickets", tags=["Escalation & Support Tickets"])


@router.post("", response_model=TicketResponse)
def create_ticket(data: TicketCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = ticket_service.create_ticket(db, student=current_user, data=data)
    return _format_ticket_response(ticket, db)


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(SupportTicket)

    if current_user.role == "student":
        query = query.filter(SupportTicket.student_id == current_user.id)
    elif current_user.role == "faculty":
        query = query.filter(SupportTicket.faculty_id == current_user.id)
    # Admin sees all

    if status_filter:
        query = query.filter(SupportTicket.status == status_filter)
    if priority_filter:
        query = query.filter(SupportTicket.priority == priority_filter)

    tickets = query.order_by(SupportTicket.created_at.desc()).all()
    return [_format_ticket_response(t, db) for t in tickets]


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    # Authorization
    if current_user.role == "student" and ticket.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to view this ticket.")

    return _format_ticket_response(ticket, db, include_messages=True)


@router.post("/{ticket_id}/messages", response_model=TicketMessageResponse)
def send_ticket_message(
    ticket_id: int,
    data: TicketMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    if current_user.role == "student" and ticket.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to participate in this ticket.")

    try:
        msg = ticket_service.add_message(
            db=db,
            ticket_id=ticket.id,
            sender=current_user,
            message_text=data.message,
            attachment_url=data.attachment_url
        )
        return TicketMessageResponse(
            id=msg.id,
            ticket_id=msg.ticket_id,
            sender_id=msg.sender_id,
            sender_name=current_user.full_name,
            sender_role=current_user.role,
            message=msg.message,
            attachment_url=msg.attachment_url,
            created_at=msg.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: int,
    data: TicketStatusUpdate,
    current_user: User = Depends(require_role(["faculty", "admin"])),
    db: Session = Depends(get_db)
):
    try:
        ticket = ticket_service.update_status(db, ticket_id=ticket_id, new_status=data.status, actor=current_user)
        return _format_ticket_response(ticket, db, include_messages=True)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{ticket_id}/assign", response_model=TicketResponse)
def reassign_ticket(
    ticket_id: int,
    data: TicketAssignUpdate,
    current_user: User = Depends(require_role(["faculty", "admin"])),
    db: Session = Depends(get_db)
):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    ticket.faculty_id = data.faculty_id
    ticket.status = "assigned"
    db.commit()
    db.refresh(ticket)
    return _format_ticket_response(ticket, db)


def _format_ticket_response(t: SupportTicket, db: Session, include_messages: bool = False) -> TicketResponse:
    msgs = []
    if include_messages and t.messages:
        for m in t.messages:
            msgs.append(TicketMessageResponse(
                id=m.id,
                ticket_id=m.ticket_id,
                sender_id=m.sender_id,
                sender_name=m.sender.full_name if m.sender else "Academic Staff",
                sender_role=m.sender.role if m.sender else "staff",
                message=m.message,
                attachment_url=m.attachment_url,
                created_at=m.created_at
            ))

    return TicketResponse(
        id=t.id,
        ticket_number=t.ticket_number,
        student_id=t.student_id,
        student_name=t.student.full_name if t.student else "Student",
        student_roll=t.student.student_profile.roll_number if t.student and t.student.student_profile else None,
        faculty_id=t.faculty_id,
        faculty_name=t.faculty.full_name if t.faculty else "Unassigned",
        department_id=t.department_id,
        department_name=t.department.name if t.department else None,
        course_id=t.course_id,
        course_name=t.course.name if t.course else None,
        conversation_id=t.conversation_id,
        subject=t.subject,
        description=t.description,
        priority=t.priority,
        status=t.status,
        created_at=t.created_at,
        updated_at=t.updated_at,
        messages_count=len(t.messages) if t.messages else 0,
        messages=msgs if include_messages else []
    )
