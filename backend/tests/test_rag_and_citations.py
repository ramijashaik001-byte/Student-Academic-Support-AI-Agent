import pytest
from app.database import SessionLocal
from app.models import DocumentChunk, Document
from app.rag.vector_store import vector_store
from app.ai.academic_agent import academic_agent


def test_vector_retrieval_and_exact_citations():
    db = SessionLocal()
    try:
        chunks = db.query(DocumentChunk).join(Document).filter(Document.is_active == True).all()
        assert len(chunks) > 0

        # Query about attendance
        res = vector_store.search("minimum attendance percentage requirement", chunks, top_k=3)
        assert len(res) > 0
        top = res[0]
        assert "Attendance" in top["document_title"] or "Academic" in top["document_title"]

        # Generate grounded response
        ans = academic_agent.generate_response(
            query="What is the minimum attendance requirement?",
            conversation_history=[],
            retrieved_sources=res,
            user_name="Ramija"
        )
        assert "75%" in ans["content"]
        assert len(ans["sources"]) > 0
        assert ans["sources"][0]["document_title"] is not None
        assert ans["sources"][0]["page_number"] is not None
        assert ans["escalation_suggested"] is False
    finally:
        db.close()


def test_unsupported_query_escalation_trigger():
    db = SessionLocal()
    try:
        # Query with zero academic document coverage
        ans = academic_agent.generate_response(
            query="What is the recipe for chicken biryani in hostel canteen?",
            conversation_history=[],
            retrieved_sources=[],  # Zero sources
            user_name="Ramija"
        )
        # Assistant must honestly declare missing info and offer escalation
        assert "couldn't find" in ans["content"].lower() or "not find" in ans["content"].lower()
        assert ans["escalation_suggested"] is True
    finally:
        db.close()
