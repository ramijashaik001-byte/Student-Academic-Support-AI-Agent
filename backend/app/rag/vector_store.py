import os
import math
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.config import settings

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except Exception:
    CHROMA_AVAILABLE = False


class HybridVectorStore:
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self._init_chroma()

    def _init_chroma(self):
        if CHROMA_AVAILABLE:
            try:
                chroma_path = str(settings.VECTOR_DIR)
                self.chroma_client = chromadb.PersistentClient(path=chroma_path)
                self.collection = self.chroma_client.get_or_create_collection(
                    name="academic_materials",
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"ChromaDB init notice: {e}. Falling back to internal hybrid index.")
                self.chroma_client = None
                self.collection = None

    def add_chunks(self, document_id: int, document_title: str, chunks: List[Dict[str, Any]], metadata: Dict[str, Any]):
        if not chunks:
            return

        # 1. Index in Chroma if available
        if self.collection:
            try:
                ids = [f"doc_{document_id}_chunk_{c['chunk_index']}" for c in chunks]
                documents = [c["content"] for c in chunks]
                metadatas = [
                    {
                        "document_id": document_id,
                        "document_title": document_title,
                        "chunk_index": c["chunk_index"],
                        "page_number": c.get("page_number", 1),
                        "section_heading": c.get("section_heading", ""),
                        "category": metadata.get("category", "general"),
                        "department_id": str(metadata.get("department_id") or ""),
                        "course_id": str(metadata.get("course_id") or ""),
                    }
                    for c in chunks
                ]
                self.collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
            except Exception as e:
                print(f"Notice: Chroma indexing warning: {e}")

    def delete_document_chunks(self, document_id: int):
        if self.collection:
            try:
                self.collection.delete(
                    where={"document_id": document_id}
                )
            except Exception as e:
                print(f"Notice: Chroma delete warning: {e}")

    def search(
        self,
        query: str,
        all_db_chunks: List[Any],  # List of DocumentChunk ORM models or dicts with document relations
        department_id: Optional[int] = None,
        course_id: Optional[int] = None,
        top_k: int = settings.RETRIEVAL_TOP_K
    ) -> List[Dict[str, Any]]:
        if not all_db_chunks:
            return []

        # 1. Try ChromaDB retrieval if available
        chroma_results = []
        if self.collection:
            try:
                query_filter = None
                if department_id and course_id:
                    query_filter = {
                        "$or": [
                            {"department_id": str(department_id)},
                            {"course_id": str(course_id)},
                            {"department_id": ""}
                        ]
                    }

                res = self.collection.query(
                    query_texts=[query],
                    n_results=min(top_k * 2, max(1, self.collection.count())),
                    where=query_filter
                )
                
                if res and res.get("documents") and len(res["documents"]) > 0:
                    docs = res["documents"][0]
                    metas = res["metadatas"][0] if res.get("metadatas") else []
                    distances = res["distances"][0] if res.get("distances") else []

                    for idx, doc in enumerate(docs):
                        meta = metas[idx] if idx < len(metas) else {}
                        dist = distances[idx] if idx < len(distances) else 0.5
                        # cosine distance to similarity
                        score = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                        chroma_results.append({
                            "document_id": int(meta.get("document_id", 0)),
                            "document_title": meta.get("document_title", "College Document"),
                            "chunk_index": int(meta.get("chunk_index", 0)),
                            "page_number": int(meta.get("page_number", 1)),
                            "section_heading": meta.get("section_heading", "Excerpt"),
                            "content": doc,
                            "relevance_score": round(score, 3)
                        })
            except Exception as e:
                print(f"Notice: Chroma query warning: {e}")

        # 2. Hybrid BM25/TF-IDF Lexical Ranker over actual DB chunks
        lexical_results = self._lexical_search(query, all_db_chunks, top_k * 2)

        # 3. Fuse results (Reciprocal Rank Fusion / Weighted Scoring)
        fused = {}
        for item in chroma_results:
            key = f"{item['document_id']}_{item['chunk_index']}"
            fused[key] = item

        for item in lexical_results:
            key = f"{item['document_id']}_{item['chunk_index']}"
            if key in fused:
                # boost existing score with lexical confirmation
                fused[key]["relevance_score"] = round(min(0.99, fused[key]["relevance_score"] * 0.6 + item["relevance_score"] * 0.4 + 0.1), 3)
            else:
                fused[key] = item

        # Sort descending by relevance score
        sorted_results = sorted(fused.values(), key=lambda x: x["relevance_score"], reverse=True)
        return sorted_results[:top_k]
    def _lexical_search(self, query: str, chunks: List[Any], top_k: int) -> List[Dict[str, Any]]:
        STOP_WORDS = {
            "what", "is", "are", "the", "a", "an", "of", "in", "for", "to", "and", "or",
            "on", "at", "by", "with", "from", "about", "can", "you", "me", "my", "how",
            "why", "which", "do", "does", "did", "have", "has", "had", "be", "been",
            "being", "this", "that", "these", "those", "it", "its", "i", "we", "they",
            "tell", "explain", "give", "show", "please", "help"
        }
        raw_tokens = re.findall(r'\b[a-zA-Z0-9_\-]{2,}\b', query.lower())
        tokens = [t for t in raw_tokens if t not in STOP_WORDS]
        if not tokens:
            tokens = raw_tokens
        if not tokens:
            return []

        # Keywords with extra academic significance
        scores = []
        for c in chunks:
            text = c.content if hasattr(c, "content") else c.get("content", "")
            title = c.document.title if hasattr(c, "document") and c.document else "Academic Document"
            doc_id = c.document_id if hasattr(c, "document_id") else c.get("document_id", 0)
            page_no = c.page_number if hasattr(c, "page_number") else c.get("page_number", 1)
            heading = c.section_heading if hasattr(c, "section_heading") else c.get("section_heading", "")
            chunk_idx = c.chunk_index if hasattr(c, "chunk_index") else c.get("chunk_index", 0)

            text_lower = text.lower()
            title_lower = title.lower()

            match_count = 0
            exact_bonus = 0.0

            for tok in tokens:
                count = text_lower.count(tok)
                if count > 0:
                    match_count += 1 + math.log(1 + count)
                if tok in title_lower:
                    exact_bonus += 0.35

            if match_count > 0 or exact_bonus > 0:
                # Normalization
                score = (match_count / (len(tokens) + 1.0)) * 0.65 + exact_bonus * 0.35
                score = min(0.98, max(0.1, score))
                scores.append({
                    "document_id": doc_id,
                    "document_title": title,
                    "chunk_index": chunk_idx,
                    "page_number": page_no,
                    "section_heading": heading,
                    "content": text,
                    "relevance_score": round(score, 3)
                })

        scores.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scores[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        chroma_count = 0
        status = "offline"
        if self.collection:
            try:
                chroma_count = self.collection.count()
                status = "healthy"
            except Exception:
                status = "degraded"

        return {
            "status": status,
            "engine": "ChromaDB + Hybrid BM25/Cosine Ranker",
            "chroma_available": CHROMA_AVAILABLE,
            "indexed_chunks_in_chroma": chroma_count
        }


vector_store = HybridVectorStore()
