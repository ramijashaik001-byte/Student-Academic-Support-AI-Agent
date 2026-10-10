import re
from typing import List, Dict, Any
from app.config import settings


class SentenceAwareChunker:
    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_into_sentences(self, text: str) -> List[str]:
        # Split on sentence boundaries while keeping sentences intact
        clean_text = re.sub(r'\r\n|\r', '\n', text)
        sentences = re.split(r'(?<=[.!?])\s+|\n{2,}', clean_text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_extracted_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        global_chunk_idx = 0

        for block in blocks:
            page_number = block.get("page_number", 1)
            section_heading = block.get("section_heading", "General")
            text = block.get("text", "")

            sentences = self.split_into_sentences(text)
            if not sentences:
                continue

            current_chunk = []
            current_len = 0

            for sentence in sentences:
                sentence_len = len(sentence)

                if current_len + sentence_len > self.chunk_size and current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunks.append({
                        "chunk_index": global_chunk_idx,
                        "page_number": page_number,
                        "section_heading": section_heading,
                        "content": chunk_text,
                        "token_count": max(1, len(chunk_text.split()))
                    })
                    global_chunk_idx += 1

                    # Keep overlap from the end of current_chunk
                    overlap_buffer = []
                    overlap_len = 0
                    for prev_sent in reversed(current_chunk):
                        if overlap_len + len(prev_sent) <= self.chunk_overlap:
                            overlap_buffer.insert(0, prev_sent)
                            overlap_len += len(prev_sent)
                        else:
                            break
                    current_chunk = overlap_buffer
                    current_len = overlap_len

                current_chunk.append(sentence)
                current_len += sentence_len

            if current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "chunk_index": global_chunk_idx,
                    "page_number": page_number,
                    "section_heading": section_heading,
                    "content": chunk_text,
                    "token_count": max(1, len(chunk_text.split()))
                })
                global_chunk_idx += 1

        return chunks
