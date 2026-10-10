from typing import Optional
from sqlalchemy.orm import Session
from app.models import SupportTicket, TicketMessage, User, Course, Department
from app.schemas import TicketCreate
from app.services.notification_service import notification_service
from app.services.audit_service import audit_service


class TicketService:
    @staticmethod
    def create_ticket(db: Session, student: User, data: TicketCreate) -> SupportTicket:
        # Determine assigned faculty
        faculty_id = None
        if data.course_id:
            course = db.query(Course).filter(Course.id == data.course_id).first()
            if course and course.subjects:
                for subj in course.subjects:
                    if subj.faculty_id:
                        faculty_id = subj.faculty_id
                        break
        
        # Fallback to any faculty in the department
        if not faculty_id and data.department_id:
            faculty_user = db.query(User).filter(User.role == "faculty").first()
            if faculty_user:
                faculty_id = faculty_user.id

        # Absolute fallback to first available faculty
        if not faculty_id:
            first_fac = db.query(User).filter(User.role == "faculty").first()
            if first_fac:
                faculty_id = first_fac.id

        # Generate ticket number
        total_count = db.query(SupportTicket).count() + 1
        ticket_number = f"TICK-2026-{total_count:04d}"

        ticket = SupportTicket(
            ticket_number=ticket_number,
            student_id=student.id,
            faculty_id=faculty_id,
            department_id=data.department_id,
            course_id=data.course_id,
            conversation_id=data.conversation_id,
            subject=data.subject,
            description=data.description,
            priority=data.priority,
            status="assigned" if faculty_id else "open"
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        # Initial message
        init_msg = TicketMessage(
            ticket_id=ticket.id,
            sender_id=student.id,
            message=data.description
        )
        db.add(init_msg)
        db.commit()

        # Notify assigned faculty
        if faculty_id:
            notification_service.create_notification(
                db=db,
                user_id=faculty_id,
                title="New Academic Support Ticket Assigned",
                message=f"Student {student.full_name} submitted ticket {ticket_number}: '{data.subject}'",
                notif_type="ticket_update",
                link_url=f"/faculty/escalations/{ticket.id}"
            )

        audit_service.log(
            db=db,
            user_id=student.id,
            action="TICKET_CREATED",
            resource_type="ticket",
            resource_id=str(ticket.id),
            details=f"Created {ticket_number} ('{data.subject}')"
        )

        return ticket

    @staticmethod
    def add_message(db: Session, ticket_id: int, sender: User, message_text: str, attachment_url: Optional[str] = None) -> TicketMessage:
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise ValueError("Ticket not found")

        msg = TicketMessage(
            ticket_id=ticket.id,
            sender_id=sender.id,
            message=message_text,
            attachment_url=attachment_url
        )
        db.add(msg)

        # Update status depending on who replied
        if sender.role in ["faculty", "admin"]:
            ticket.status = "waiting_for_student"
            # Notify student
            notification_service.create_notification(
                db=db,
                user_id=ticket.student_id,
                title="Faculty Responded to Your Ticket",
                message=f"{sender.full_name} replied to ticket {ticket.ticket_number}.",
                notif_type="ticket_update",
                link_url=f"/student/tickets"
            )
        else:
            ticket.status = "in_progress"
            # Notify faculty
            if ticket.faculty_id:
                notification_service.create_notification(
                    db=db,
                    user_id=ticket.faculty_id,
                    title="Student Replied on Ticket",
                    message=f"{sender.full_name} replied to ticket {ticket.ticket_number}.",
                    notif_type="ticket_update",
                    link_url=f"/faculty/escalations/{ticket.id}"
                )

        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def update_status(db: Session, ticket_id: int, new_status: str, actor: User) -> SupportTicket:
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise ValueError("Ticket not found")

        old_status = ticket.status
        ticket.status = new_status
        db.commit()
        db.refresh(ticket)

        # Notify student
        notification_service.create_notification(
            db=db,
            user_id=ticket.student_id,
            title="Ticket Status Updated",
            message=f"Your ticket {ticket.ticket_number} is now marked as '{new_status.replace('_', ' ').title()}'.",
            notif_type="ticket_update",
            link_url=f"/student/tickets"
        )

        audit_service.log(
            db=db,
            user_id=actor.id,
            action="TICKET_STATUS_UPDATED",
            resource_type="ticket",
            resource_id=str(ticket.id),
            details=f"Status changed from {old_status} to {new_status} by {actor.full_name}"
        )
        return ticket


ticket_service = TicketService()
