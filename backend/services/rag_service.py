"""
RAG Service — document ingestion, chunking, semantic retrieval, and citations.
Extends the built-in TF-IDF knowledge base with user-uploaded documents.
"""

from __future__ import annotations

import hashlib
import logging
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("data/rag_uploads")
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80


def _tokenize(text: str) -> List[str]:
    text = text.lower()
    tokens = re.findall(r"\b[a-z][a-z0-9]*\b", text)
    stop = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "it", "its", "this", "that", "these",
        "those", "as", "or", "and", "but", "if", "not", "than", "more", "also",
    }
    return [t for t in tokens if t not in stop and len(t) > 2]


def _chunk_text(text: str, source_id: str, title: str) -> List[Dict[str, Any]]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    chunks: List[Dict[str, Any]] = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        piece = text[start:end].strip()
        if len(piece) > 40:
            chunks.append({
                "id": f"{source_id}_chunk_{idx}",
                "topic": title,
                "content": piece,
                "tags": [title.lower(), source_id],
                "source_file": source_id,
            })
            idx += 1
        if end >= len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks


class RAGDocumentStore:
    """Manages uploaded documents and merges them into TF-IDF retrieval."""

    def __init__(self):
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self._extra_docs: List[Dict[str, Any]] = []
        self._load_persisted()

    def _load_persisted(self) -> None:
        for path in sorted(UPLOAD_DIR.glob("*.txt")):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                doc_id = path.stem
                self._extra_docs.extend(_chunk_text(text, doc_id, path.name))
            except Exception as exc:
                logger.warning("Could not load RAG file %s: %s", path, exc)

    def list_documents(self) -> List[Dict[str, str]]:
        docs = []
        seen = set()
        for d in self._extra_docs:
            fid = d.get("source_file", "")
            if fid and fid not in seen:
                seen.add(fid)
                docs.append({
                    "id": fid,
                    "name": d.get("topic", fid),
                    "chunks": sum(1 for x in self._extra_docs if x.get("source_file") == fid),
                })
        return docs

    def add_document(self, filename: str, content: str) -> Dict[str, Any]:
        safe_name = re.sub(r"[^\w.\-]", "_", filename)[:120]
        doc_hash = hashlib.md5(content.encode("utf-8", errors="ignore")).hexdigest()[:10]
        doc_id = f"{Path(safe_name).stem}_{doc_hash}"

        self._extra_docs = [d for d in self._extra_docs if d.get("source_file") != doc_id]
        new_chunks = _chunk_text(content, doc_id, safe_name)
        if not new_chunks:
            raise ValueError("Document is empty or too short to index.")

        self._extra_docs.extend(new_chunks)
        out_path = UPLOAD_DIR / f"{doc_id}.txt"
        out_path.write_text(content, encoding="utf-8")

        logger.info("Indexed RAG document %s (%d chunks)", safe_name, len(new_chunks))
        return {
            "id": doc_id,
            "name": safe_name,
            "chunks": len(new_chunks),
            "indexed_at": datetime.utcnow().isoformat(),
        }

    def remove_document(self, doc_id: str) -> bool:
        before = len(self._extra_docs)
        self._extra_docs = [d for d in self._extra_docs if d.get("source_file") != doc_id]
        path = UPLOAD_DIR / f"{doc_id}.txt"
        if path.exists():
            path.unlink()
        return len(self._extra_docs) < before

    def get_extra_documents(self) -> List[Dict[str, Any]]:
        return list(self._extra_docs)

    def summarize_documents(self, max_chars: int = 600) -> str:
        if not self._extra_docs:
            return "No custom documents uploaded yet. Upload supply chain SOPs, SLA docs, or runbooks to enrich AI answers."
        by_file: Dict[str, List[str]] = {}
        for d in self._extra_docs:
            by_file.setdefault(d.get("source_file", "doc"), []).append(d["content"])
        parts = []
        for fid, chunks in by_file.items():
            preview = " ".join(chunks)[:max_chars // max(len(by_file), 1)]
            parts.append(f"**{fid}**: {preview[:200]}…")
        return "\n\n".join(parts)
