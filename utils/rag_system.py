"""Retrieval system for the Student Support Assistant.

Semantic search: documents and queries are converted to embedding vectors and
ranked by cosine similarity. If the embedding library is not installed, the
system falls back to keyword matching so the app still runs.
"""
import json
import os
import re
from typing import Dict, List, Optional

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STOPWORDS = {
    "the", "and", "for", "are", "was", "were", "what", "when", "where", "who", "why", "how", "can", "could",
    "should", "would", "will", "does", "did", "has", "have", "had", "any", "all", "you", "your", "our", "this",
    "that", "with", "from", "about", "into", "there", "their", "them", "than", "then", "its", "not", "but", "get",
}
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class FastEmbedder:
    """Small, CPU-only embedding model (ONNX, no PyTorch needed)."""

    def __init__(self, model_name: Optional[str] = None):
        from fastembed import TextEmbedding  # imported here so it stays optional

        self.model = TextEmbedding(model_name or os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5"))

    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.clip(norms, 1e-12, None)

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        return self._normalize(np.array(list(self.model.embed(texts)), dtype=np.float32))

    def embed_query(self, text: str) -> np.ndarray:
        return self.embed_documents([QUERY_PREFIX + text])[0]


def _to_text(value) -> str:
    """Turn lists and dicts from the JSON files into readable text."""
    if isinstance(value, dict):
        return ", ".join(f"{k.replace('_', ' ')}: {_to_text(v)}" for k, v in value.items())
    if isinstance(value, list):
        return ", ".join(_to_text(v) for v in value)
    return str(value)


class RAGSystem:
    """Retrieval for the knowledge base, FAQs, regulations and syllabi."""

    def __init__(self, embedder="auto"):
        self.knowledge_base = self._load("knowledge_base.json", [])
        self.faqs = self._load("faqs.json", [])
        self.syllabus = self._load("syllabus.json", {})
        self.regulations = self._load("regulations.json", [])

        self.documents = self._build_corpus()
        self.min_score = float(os.getenv("MIN_SCORE", "0.5"))
        # Hybrid search: final score = semantic similarity + KEYWORD_WEIGHT * keyword overlap
        self.keyword_weight = float(os.getenv("KEYWORD_WEIGHT", "0.15"))

        self.embedder = self._init_embedder(embedder)
        self.doc_vectors = None
        if self.embedder is not None:
            texts = [d["embed_text"] for d in self.documents]
            self.doc_vectors = self.embedder.embed_documents(texts)

    # ---------- loading ----------
    @staticmethod
    def _load(filename: str, default):
        path = os.path.join(DATA_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return default

    @staticmethod
    def _init_embedder(embedder):
        if embedder != "auto":
            return embedder  # None (keyword mode) or a custom embedder
        try:
            return FastEmbedder()
        except Exception as exc:  # library missing or model download failed
            print(f"[RAG] Semantic search unavailable ({exc}). Using keyword search.")
            return None

    def _build_corpus(self) -> List[Dict]:
        """Put every source (knowledge base, FAQs, regulations, syllabus) in one list."""
        docs = []
        for d in self.knowledge_base:
            keywords = " ".join(d.get("keywords", []))
            docs.append({"source": "knowledge_base", "title": d["title"], "content": d["content"],
                         "category": d.get("category", "General"), "keywords": d.get("keywords", []),
                         "embed_text": f"{d['title']}. {d['content']} {keywords}"})
        for d in self.faqs:
            docs.append({"source": "faq", "title": d["question"], "content": d["answer"],
                         "question": d["question"], "answer": d["answer"],
                         "category": d.get("category", "FAQ"),
                         "embed_text": f"{d['question']} {d['answer']}"})
        for d in self.regulations:
            docs.append({"source": "regulation", "title": d["title"], "content": d["content"],
                         "category": d.get("category", "Regulation"),
                         "embed_text": f"{d['title']}. {d['content']}"})
        for key, c in self.syllabus.items():
            content = (f"{c.get('code', '')} {c.get('title', '')}. Instructor: {c.get('instructor', '')}. "
                       f"Credits: {c.get('credits', '')}. Semester: {c.get('semester', '')}. "
                       f"Topics: {_to_text(c.get('topics', []))}. Assessment: {_to_text(c.get('assessment', ''))}. "
                       f"Office hours: {c.get('office_hours', '')}. Textbook: {c.get('textbook', '')}.")
            docs.append({"source": "syllabus", "title": c.get("title", key), "content": content,
                         "category": "Syllabus", "embed_text": content})
        return docs

    # ---------- retrieval ----------
    def retrieve(self, query: str, top_k: int = 3, min_score: Optional[float] = None) -> List[Dict]:
        """Return the most relevant documents, best first. Each has 'score' and 'source'."""
        if self.embedder is not None:
            threshold = self.min_score if min_score is None else min_score
            scored = self._semantic_scores(query)
            keep = lambda score: score >= threshold
        else:
            threshold = 0.0 if min_score is None else min_score  # keyword scores use their own scale
            scored = self._keyword_scores(query)
            keep = lambda score: score > threshold

        scored.sort(key=lambda pair: pair[0], reverse=True)
        results = []
        for score, doc in scored[:top_k]:
            if keep(score):
                item = {k: v for k, v in doc.items() if k != "embed_text"}
                item["score"] = round(float(score), 4)
                results.append(item)
        return results

    def _semantic_scores(self, query: str):
        query_vector = self.embedder.embed_query(query)
        similarities = self.doc_vectors @ query_vector
        scored = []
        for sim, doc in zip(similarities, self.documents):
            score = float(sim) + self.keyword_weight * self._keyword_overlap(query, doc)
            scored.append((score, doc))
        return scored

    @staticmethod
    def _tokens(text: str):
        """Lowercase content words with a very simple plural fix (days -> day)."""
        words = [w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2 and w not in STOPWORDS]
        return [w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words]

    def _keyword_overlap(self, query: str, doc: Dict) -> float:
        """0 to 1: share of the query's words found in the document.
        Words in the title or keywords count fully, words only in the body count half."""
        query_words = self._tokens(query)
        if not query_words:
            return 0.0
        strong = set(self._tokens(doc["title"] + " " + " ".join(doc.get("keywords", []))))
        weak = set(self._tokens(doc["content"]))
        total = sum(1.0 if w in strong else 0.5 if w in weak else 0.0 for w in query_words)
        return total / len(query_words)

    def _keyword_scores(self, query: str):
        words = [w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 2 and w not in STOPWORDS]
        scored = []
        for doc in self.documents:
            title, content = doc["title"].lower(), doc["content"].lower()
            score = sum(3.0 for w in words if w in title) + sum(1.0 for w in words if w in content)
            scored.append((score, doc))
        return scored

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search with detailed results (used by /api/search)."""
        return [{"title": r["title"], "content": r["content"], "type": r["source"],
                 "category": r.get("category", "General"), "score": r["score"]}
                for r in self.retrieve(query, top_k)]

    # ---------- direct getters (used by the API) ----------
    def get_faqs(self) -> List[Dict]:
        return self.faqs

    def get_syllabus(self, subject: str) -> Dict:
        return self.syllabus.get(subject.lower(), {})

    def get_regulations(self) -> List[Dict]:
        return self.regulations
