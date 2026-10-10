import pytest
from pathlib import Path
from app.rag.extractors import DocumentExtractor
from app.rag.chunker import SentenceAwareChunker
from app.config import settings


def test_txt_extractor():
    txt_path = settings.SAMPLE_DOCS_DIR / "Lab_Safety_and_Project_Submission_Guidelines.txt"
    blocks = DocumentExtractor.extract_content(txt_path)
    assert len(blocks) > 0
    assert any("SAFETY" in b["text"].upper() for b in blocks)


def test_csv_extractor():
    csv_path = settings.SAMPLE_DOCS_DIR / "Academic_Calendar_Fall_2026.csv"
    blocks = DocumentExtractor.extract_content(csv_path)
    assert len(blocks) > 0
    assert any("Semester" in b["text"] for b in blocks)


def test_pdf_extractor():
    pdf_path = settings.SAMPLE_DOCS_DIR / "Academic_Regulations_and_Attendance_Policy_2026.pdf"
    blocks = DocumentExtractor.extract_content(pdf_path)
    assert len(blocks) >= 2
    assert any("75%" in b["text"] for b in blocks)


def test_docx_extractor():
    docx_path = settings.SAMPLE_DOCS_DIR / "CS301_Operating_Systems_Syllabus_and_Deadlines.docx"
    blocks = DocumentExtractor.extract_content(docx_path)
    assert len(blocks) > 0
    assert any("Scheduling" in b["text"] for b in blocks)


def test_invalid_extension():
    fake_path = settings.BASE_DIR / "fake.exe"
    fake_path.write_text("dummy")
    try:
        with pytest.raises(ValueError) as exc:
            DocumentExtractor.validate_file(fake_path)
        assert "Unsupported file format" in str(exc.value)
    finally:
        fake_path.unlink()


def test_sentence_aware_chunker():
    chunker = SentenceAwareChunker(chunk_size=100, chunk_overlap=20)
    sample_block = [{
        "page_number": 1,
        "section_heading": "Test Section",
        "text": "The quick brown fox jumps over the lazy dog. A second sentence discusses attendance. A third sentence provides exam dates."
    }]
    chunks = chunker.chunk_extracted_blocks(sample_block)
    assert len(chunks) >= 2
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["section_heading"] == "Test Section"
    assert "token_count" in chunks[0]
