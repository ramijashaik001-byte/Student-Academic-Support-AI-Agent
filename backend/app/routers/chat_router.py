from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import User, Conversation, ChatMessage, AnswerSource, Document, DocumentChunk
from app.schemas import (
    ChatAskRequest, ChatMessageResponse, ConversationResponse,
    ConversationDetailResponse, ChatFeedbackRequest, AnswerSourceResponse
)
from app.dependencies import get_current_user
from app.rag.vector_store import vector_store
from app.ai.academic_agent import academic_agent

router = APIRouter(prefix="/api/chat", tags=["Chat Assistant"])


@router.post("", response_model=ChatMessageResponse)
def ask_question(data: ChatAskRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Fetch or initialize conversation (enforce student isolation)
    if data.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == data.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found or unauthorized.")
    else:
        # Generate friendly title from first 6 words
        words = data.message.strip().split()
        title_summary = " ".join(words[:6]) + ("..." if len(words) > 6 else "")
        conversation = Conversation(
            user_id=current_user.id,
            title=title_summary or "Academic Inquiry"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 2. Extract recent conversation memory for follow-up context
    recent_db_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation.id)
        .order_by(desc(ChatMessage.created_at))
        .limit(6)
        .all()
    )
    # Reverse to chronological order
    recent_db_messages.reverse()
    history = [{"sender": m.sender, "content": m.content} for m in recent_db_messages]

    # 2.5 Classify question category
    from app.ai.question_classifier import QuestionClassifier, QuestionCategory
    category, meta = QuestionClassifier.classify(data.message, history=history)

    # 3. Retrieve authorized document chunks (only for syllabus/document/regulation queries)
    retrieved_sources = []
    if category in [QuestionCategory.DOCUMENT_SYLLABUS, QuestionCategory.CURRICULUM_REGULATION]:
        active_chunks = (
            db.query(DocumentChunk)
            .join(Document)
            .filter(Document.is_active == True, Document.status == "indexed")
            .all()
        )
        search_query = data.message
        if history and len(data.message.split()) <= 6:
            prev_user_msgs = [h["content"] for h in history if h["sender"] == "user"]
            if prev_user_msgs:
                search_query = f"{prev_user_msgs[-1]} {data.message}"

        department_id = current_user.student_profile.department_id if current_user.student_profile else None
        retrieved_sources = vector_store.search(
            query=search_query,
            all_db_chunks=active_chunks,
            department_id=department_id,
            course_id=data.course_id,
            top_k=4
        )

    # 4. Generate AI academic response
    agent_output = academic_agent.generate_response(
        query=data.message,
        conversation_history=history,
        retrieved_sources=retrieved_sources,
        user_name=current_user.full_name,
        db=db,
        student_id=current_user.id,
        category=category,
        meta=meta
    )

    # 5. Persist user message
    user_msg = ChatMessage(
        conversation_id=conversation.id,
        sender="user",
        content=data.message
    )
    db.add(user_msg)
    db.commit()

    # 6. Persist assistant response
    asst_msg = ChatMessage(
        conversation_id=conversation.id,
        sender="assistant",
        content=agent_output["content"],
        confidence_score=agent_output["confidence_score"],
        escalation_suggested=agent_output["escalation_suggested"]
    )
    db.add(asst_msg)
    db.commit()
    db.refresh(asst_msg)

    # 7. Persist source citations
    persisted_sources = []
    for s in agent_output.get("sources", []):
        src_obj = AnswerSource(
            message_id=asst_msg.id,
            document_id=s.get("document_id"),
            document_title=s.get("document_title", "Official Academic Material"),
            page_number=s.get("page_number", 1),
            section=s.get("section", "General"),
            excerpt=s.get("excerpt", ""),
            relevance_score=s.get("relevance_score", 0.9)
        )
        db.add(src_obj)
        persisted_sources.append(src_obj)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    db.commit()

    return ChatMessageResponse(
        id=asst_msg.id,
        conversation_id=conversation.id,
        sender="assistant",
        content=asst_msg.content,
        confidence_score=asst_msg.confidence_score,
        escalation_suggested=asst_msg.escalation_suggested,
        feedback_rating=None,
        feedback_comment=None,
        sources=[AnswerSourceResponse.model_validate(s) for s in persisted_sources],
        follow_up_suggestions=agent_output.get("follow_up_suggestions", []),
        created_at=asst_msg.created_at
    )


@router.post("/messages/{message_id}/feedback")
def submit_feedback(message_id: int, feedback: ChatFeedbackRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found.")

    msg.feedback_rating = feedback.rating
    msg.feedback_comment = feedback.comment
    db.commit()
    return {"message": "Thank you! Your feedback helps us improve academic responses."}


# ---------------- Conversation Management ----------------
@router.get("/conversations", response_model=List[ConversationResponse])
def get_user_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.updated_at))
        .all()
    )

    result = []
    for c in convs:
        last_m = db.query(ChatMessage).filter(ChatMessage.conversation_id == c.id).order_by(desc(ChatMessage.created_at)).first()
        m_count = db.query(ChatMessage).filter(ChatMessage.conversation_id == c.id).count()
        result.append(ConversationResponse(
            id=c.id,
            user_id=c.user_id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            last_message=last_m.content[:80] + "..." if last_m else None,
            message_count=m_count
        ))
    return result


@router.post("/conversations", response_model=ConversationResponse)
def create_new_conversation(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = Conversation(
        user_id=current_user.id,
        title="New Academic Discussion"
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        last_message=None,
        message_count=0
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation_detail(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conv.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    formatted_msgs = []
    for m in msgs:
        formatted_msgs.append(ChatMessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            sender=m.sender,
            content=m.content,
            confidence_score=m.confidence_score,
            escalation_suggested=m.escalation_suggested,
            feedback_rating=m.feedback_rating,
            feedback_comment=m.feedback_comment,
            sources=[AnswerSourceResponse.model_validate(s) for s in m.sources],
            follow_up_suggestions=[],
            created_at=m.created_at
        ))

    return ConversationDetailResponse(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=formatted_msgs
    )


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted successfully."}
