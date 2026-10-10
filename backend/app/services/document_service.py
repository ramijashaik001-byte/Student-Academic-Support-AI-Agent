import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Document, DocumentChunk, User
from app.rag.extractors import DocumentExtractor
from app.rag.chunker import SentenceAwareChunker
from app.rag.vector_store import vector_store
from app.services.audit_service import audit_service


class DocumentService:
    def __init__(self):
        self.chunker = SentenceAwareChunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)

    def process_and_index_document(self, db: Session, doc_id: int) -> bool:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return False

        doc.status = "processing"
        doc.error_message = None
        db.commit()

        file_path = Path(doc.file_path)
        try:
            # 1. Extract content blocks
            blocks = DocumentExtractor.extract_content(file_path)
            
            # 2. Sentence-aware chunking
            chunks_data = self.chunker.chunk_extracted_blocks(blocks)
            if not chunks_data:
                raise ValueError("No viable text chunks could be generated from document content.")

            # 3. Clean old chunks if reindexing
            db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
            vector_store.delete_document_chunks(doc.id)

            # 4. Insert chunks into DB
            db_chunks = []
            for c in chunks_data:
                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=c["chunk_index"],
                    page_number=c.get("page_number", 1),
                    section_heading=c.get("section_heading", "General"),
                    content=c["content"],
                    token_count=c.get("token_count", 0)
                )
                db_chunks.append(chunk_obj)
            
            db.add_all(db_chunks)
            
            # 5. Index into Vector Store
            vector_store.add_chunks(
                document_id=doc.id,
                document_title=doc.title,
                chunks=chunks_data,
                metadata={
                    "category": doc.category,
                    "department_id": doc.department_id,
                    "course_id": doc.course_id,
                }
            )

            doc.status = "indexed"
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            doc.status = "failed"
            doc.error_message = str(e)
            db.commit()
            print(f"Document processing failed for ID {doc_id}: {e}")
            return False

    def save_and_create_document(
        self,
        db: Session,
        uploader: User,
        title: str,
        file_name: str,
        file_bytes: bytes,
        category: str = "general",
        department_id: Optional[int] = None,
        course_id: Optional[int] = None,
        academic_year: str = "2025-2026",
        access_level: str = "all"
    ) -> Document:
        ext = Path(file_name).suffix.lower()
        if ext not in {".pdf", ".docx", ".txt", ".csv"}:
            raise ValueError(f"Unsupported file format '{ext}'. Must be .pdf, .docx, .txt, or .csv")

        # Save to disk
        safe_file_name = f"doc_{uploader.id}_{int(os.times().system*1000)}_{file_name}"
        save_path = settings.UPLOAD_DIR / safe_file_name
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        # Validate file content
        DocumentExtractor.validate_file(save_path)

        doc = Document(
            title=title,
            file_name=file_name,
            file_path=str(save_path),
            file_type=ext.lstrip("."),
            file_size=len(file_bytes),
            category=category,
            department_id=department_id,
            course_id=course_id,
            academic_year=academic_year,
            access_level=access_level,
            status="uploaded",
            uploaded_by=uploader.id,
            version=1,
            is_active=True
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        audit_service.log(
            db=db,
            user_id=uploader.id,
            action="DOCUMENT_UPLOAD",
            resource_type="document",
            resource_id=str(doc.id),
            details=f"Uploaded '{title}' ({file_name}, {len(file_bytes)} bytes)"
        )

        # Process and index immediately
        self.process_and_index_document(db, doc.id)
        db.refresh(doc)
        return doc


document_service = DocumentService()
