import os
import csv
from pathlib import Path
from typing import List, Dict, Any
import pypdf
import docx

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv"}
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


class DocumentExtractor:

    @staticmethod
    def validate_file(file_path: Path) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ext = file_path.suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}")
        
        size = file_path.stat().st_size
        if size == 0:
            raise ValueError("File is empty.")
        if size > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File size exceeds maximum permitted limit of 25 MB ({size / (1024*1024):.1f} MB)")

    @classmethod
    def extract_content(cls, file_path: Path) -> List[Dict[str, Any]]:
        cls.validate_file(file_path)
        ext = file_path.suffix.lower()

        if ext == ".pdf":
            return cls._extract_pdf(file_path)
        elif ext == ".docx":
            return cls._extract_docx(file_path)
        elif ext == ".txt":
            return cls._extract_txt(file_path)
        elif ext == ".csv":
            return cls._extract_csv(file_path)
        else:
            raise ValueError(f"Unsupported extension {ext}")

    @staticmethod
    def _extract_pdf(file_path: Path) -> List[Dict[str, Any]]:
        results = []
        try:
            reader = pypdf.PdfReader(str(file_path))
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                text = text.strip()
                if text:
                    results.append({
                        "page_number": page_idx + 1,
                        "section_heading": f"Page {page_idx + 1}",
                        "text": text
                    })
        except Exception as e:
            raise RuntimeError(f"Error parsing PDF file: {str(e)}")
        
        if not results:
            raise ValueError("No extractable text found in PDF file.")
        return results

    @staticmethod
    def _extract_docx(file_path: Path) -> List[Dict[str, Any]]:
        results = []
        try:
            doc = docx.Document(str(file_path))
            current_heading = "General"
            buffer = []
            page_num = 1

            for p in doc.paragraphs:
                text = p.text.strip()
                if not text:
                    continue
                
                # Check if paragraph is a heading
                if p.style and ("Heading" in p.style.name or "Title" in p.style.name):
                    if buffer:
                        results.append({
                            "page_number": page_num,
                            "section_heading": current_heading,
                            "text": "\n".join(buffer)
                        })
                        buffer = []
                    current_heading = text
                else:
                    buffer.append(text)

            if buffer:
                results.append({
                    "page_number": page_num,
                    "section_heading": current_heading,
                    "text": "\n".join(buffer)
                })
        except Exception as e:
            raise RuntimeError(f"Error parsing DOCX file: {str(e)}")

        if not results:
            raise ValueError("No extractable text found in DOCX file.")
        return results

    @staticmethod
    def _extract_txt(file_path: Path) -> List[Dict[str, Any]]:
        try:
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = file_path.read_text(encoding="latin-1")
            
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            results = []
            current_heading = "Document Content"
            for idx, para in enumerate(paragraphs):
                # Detect heading if line starts with # or uppercase
                lines = para.split("\n")
                first_line = lines[0].strip()
                if first_line.startswith("#") or (len(first_line) < 60 and first_line.isupper()):
                    current_heading = first_line.lstrip("#").strip()
                
                results.append({
                    "page_number": 1 + (idx // 4),
                    "section_heading": current_heading,
                    "text": para
                })
            return results
        except Exception as e:
            raise RuntimeError(f"Error reading text file: {str(e)}")

    @staticmethod
    def _extract_csv(file_path: Path) -> List[Dict[str, Any]]:
        results = []
        try:
            try:
                f = open(file_path, "r", encoding="utf-8", newline="")
                reader = csv.DictReader(f)
            except UnicodeDecodeError:
                f = open(file_path, "r", encoding="latin-1", newline="")
                reader = csv.DictReader(f)

            with f:
                rows = list(reader)
                if not rows:
                    raise ValueError("CSV file is empty or missing headers.")
                
                # Group rows in sets of 5
                batch = []
                for i, row in enumerate(rows):
                    row_desc = " | ".join([f"{k}: {v}" for k, v in row.items() if v])
                    batch.append(row_desc)
                    if len(batch) >= 5 or i == len(rows) - 1:
                        results.append({
                            "page_number": (i // 20) + 1,
                            "section_heading": f"Records {i - len(batch) + 2} to {i + 1}",
                            "text": "\n".join(batch)
                        })
                        batch = []
            return results
        except Exception as e:
            raise RuntimeError(f"Error parsing CSV file: {str(e)}")
