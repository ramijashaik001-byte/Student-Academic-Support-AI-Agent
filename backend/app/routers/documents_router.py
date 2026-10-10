from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document, DocumentChunk, User
from app.schemas import DocumentResponse
from app.dependencies import get_current_user, require_role
from app.services.document_service import document_service
from app.rag.vector_store import vector_store

router = APIRouter(prefix="/api/documents", tags=["Knowledge Base & Documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("general"),
    department_id: Optional[int] = Form(None),
    course_id: Optional[int] = Form(None),
    academic_year: str = Form("2025-2026"),
    access_level: str = Form("all"),
    current_user: User = Depends(require_role(["faculty", "admin"])),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        doc = document_service.save_and_create_document(
            db=db,
            uploader=current_user,
            title=title,
            file_name=file.filename or "uploaded_document",
            file_bytes=content,
            category=category,
            department_id=department_id,
            course_id=course_id,
            academic_year=academic_year,
            access_level=access_level
        )
        return _format_doc_response(doc, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload processing failed: {str(e)}"
        )


@router.get("", response_model=List[DocumentResponse])
def list_documents(
    category: Optional[str] = None,
    department_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Document).filter(Document.is_active == True)
    
    if category:
        query = query.filter(Document.category == category)
    if department_id:
        query = query.filter(Document.department_id == department_id)
    
    # Non-admin access control
    if current_user.role == "student":
        query = query.filter(Document.access_level.in_(["all", "student"]))

    docs = query.order_by(Document.created_at.desc()).all()
    return [_format_doc_response(d, db) for d in docs]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_details(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id, Document.is_active == True).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return _format_doc_response(doc, db)


@router.get("/{document_id}/status")
def get_document_status(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {
        "id": doc.id,
        "title": doc.title,
        "status": doc.status,
        "error_message": doc.error_message,
        "chunks_count": db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
    }


@router.post("/{document_id}/reindex")
def reindex_document(
    document_id: int,
    current_user: User = Depends(require_role(["faculty", "admin"])),
    db: Session = Depends(get_db)
):
    success = document_service.process_and_index_document(db, document_id)
    if not success:
        raise HTTPException(status_code=500, detail="Reindexing failed. Inspect document error status.")
    return {"message": "Document re-processed and indexed successfully."}


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(require_role(["faculty", "admin"])),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Faculty can only delete their own uploaded documents unless admin
    if current_user.role == "faculty" and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete documents you personally uploaded.")

    # Remove from vector store
    vector_store.delete_document_chunks(doc.id)
    doc.is_active = False
    db.commit()
    return {"message": "Document archived and de-indexed successfully."}


def _format_doc_response(doc: Document, db: Session) -> DocumentResponse:
    chunks_c = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        file_name=doc.file_name,
        file_type=doc.file_type,
        file_size=doc.file_size,
        category=doc.category,
        department_id=doc.department_id,
        department_name=doc.department.name if doc.department else None,
        course_id=doc.course_id,
        course_code=doc.course.code if doc.course else None,
        academic_year=doc.academic_year,
        access_level=doc.access_level,
        status=doc.status,
        error_message=doc.error_message,
        uploaded_by=doc.uploaded_by,
        uploader_name=doc.uploader.full_name if doc.uploader else "Faculty Staff",
        chunks_count=chunks_c,
        version=doc.version,
        created_at=doc.created_at,
        updated_at=doc.updated_at
    )
