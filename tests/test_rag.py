"""Tests for the retrieval system. They use a tiny word-overlap embedder, so no model download is needed."""
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.rag_system import STOPWORDS, RAGSystem  # noqa: E402


class WordOverlapEmbedder:
    """Test stand-in for the real model: hashes words into a small vector."""
    DIM = 512

    def _vec(self, text):
        v = np.zeros(self.DIM, dtype=np.float32)
        for w in re.findall(r"[a-z0-9]+", text.lower()):
            if len(w) > 2 and w not in STOPWORDS:
                v[hash(w) % self.DIM] += 1.0
        n = np.linalg.norm(v)
        return v / n if n else v

    def embed_documents(self, texts):
        return np.array([self._vec(t) for t in texts])

    def embed_query(self, text):
        return self._vec(text)


def make_rag(embedder="stub"):
    return RAGSystem(embedder=WordOverlapEmbedder() if embedder == "stub" else embedder)


def test_corpus_includes_all_sources():
    rag = make_rag()
    sources = {d["source"] for d in rag.documents}
    assert sources == {"knowledge_base", "faq", "regulation", "syllabus"}
    assert len(rag.documents) == 37


def test_semantic_mode_finds_attendance_policy():
    rag = make_rag()
    results = rag.retrieve("What is the attendance requirement?", top_k=3, min_score=0.1)
    assert "Attendance Policy" in [r["title"] for r in results]


def test_regulations_and_syllabus_are_searchable():
    rag = make_rag()
    reg = rag.retrieve("academic integrity plagiarism cheating", top_k=3, min_score=0.1)
    assert any(r["source"] == "regulation" for r in reg)
    syl = rag.retrieve("cloud computing AWS course instructor", top_k=3, min_score=0.1)
    assert any(r["source"] == "syllabus" for r in syl)


def test_off_topic_query_returns_nothing():
    rag = make_rag()
    assert rag.retrieve("capital of France", top_k=3, min_score=0.3) == []


def test_results_have_score_and_source_and_are_sorted():
    rag = make_rag()
    results = rag.retrieve("library books borrow", top_k=3, min_score=0.0)
    assert results and all("score" in r and "source" in r for r in results)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_keyword_fallback_works_without_embedder():
    rag = make_rag(embedder=None)
    results = rag.retrieve("hostel application", top_k=3)
    assert results and any("hostel" in r["title"].lower() for r in results)


def test_top_k_limit():
    rag = make_rag()
    assert len(rag.retrieve("course", top_k=2, min_score=0.0)) <= 2


def test_keyword_weight_boosts_title_matches():
    rag = make_rag()
    rag.keyword_weight = 0.0
    base = {r["title"]: r["score"] for r in rag.retrieve("attendance policy", top_k=5, min_score=0.0)}
    rag.keyword_weight = 0.5
    boosted = {r["title"]: r["score"] for r in rag.retrieve("attendance policy", top_k=5, min_score=0.0)}
    assert boosted["Attendance Policy"] > base["Attendance Policy"]


def test_keyword_overlap_is_between_0_and_1():
    rag = make_rag()
    for doc in rag.documents:
        assert 0.0 <= rag._keyword_overlap("how many days of class can i miss", doc) <= 1.0
