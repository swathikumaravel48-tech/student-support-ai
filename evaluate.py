"""Measure retrieval quality.

  python evaluate.py          -> detailed report with the current settings
  python evaluate.py --sweep  -> compare different KEYWORD_WEIGHT values

Edit eval_questions.json to add your own questions."""
import json
import os
import sys

from utils.rag_system import RAGSystem

rag = RAGSystem()
mode = "semantic (embeddings)" if rag.embedder is not None else "keyword fallback"

with open(os.path.join(os.path.dirname(__file__), "eval_questions.json"), encoding="utf-8") as f:
    data = json.load(f)


def is_hit(results, expected):
    return any(e.lower() in r["title"].lower() for r in results for e in expected)


def run(verbose):
    top1 = top3 = 0
    if verbose:
        print("IN-SCOPE QUESTIONS")
    for item in data["in_scope"]:
        results = rag.retrieve(item["q"], top_k=3, min_score=0.0)
        hit1, hit3 = is_hit(results[:1], item["expected"]), is_hit(results, item["expected"])
        top1 += hit1
        top3 += hit3
        if verbose:
            best = results[0] if results else {"title": "-", "score": 0}
            print(f"{'OK ' if hit1 else ('~  ' if hit3 else 'MISS')} {item['q']}  ->  {best['title'][:45]} ({best['score']})")

    rejected = 0
    if verbose:
        print("\nOUT-OF-SCOPE QUESTIONS (best score should be LOW)")
    for q in data["out_of_scope"]:
        results = rag.retrieve(q, top_k=1, min_score=0.0)
        score = results[0]["score"] if results else 0
        ok = (score < rag.min_score) if rag.embedder is not None else (not rag.retrieve(q, top_k=1))
        rejected += ok
        if verbose:
            print(f"{'OK ' if ok else 'BAD'} {q}  ->  best score {score}")
    return top1, top3, rejected


n, m = len(data["in_scope"]), len(data["out_of_scope"])

if "--sweep" in sys.argv:
    print(f"Mode: {mode}  (MIN_SCORE = {rag.min_score})\n")
    print("KEYWORD_WEIGHT | Top-1      | Top-3      | Off-topic rejected")
    for weight in [0.0, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5]:
        rag.keyword_weight = weight
        t1, t3, rj = run(verbose=False)
        print(f"{weight:<14} | {t1}/{n} = {t1 / n:.0%} | {t3}/{n} = {t3 / n:.0%} | {rj}/{m}")
    print("\nPick the weight with the best Top-1 where off-topic questions are still rejected,")
    print("then set KEYWORD_WEIGHT in your .env file.")
else:
    print(f"Mode: {mode}  (KEYWORD_WEIGHT = {rag.keyword_weight}, MIN_SCORE = {rag.min_score})\n")
    t1, t3, rj = run(verbose=True)
    print(f"\nTop-1 accuracy: {t1}/{n} = {t1 / n:.0%}")
    print(f"Top-3 accuracy: {t3}/{n} = {t3 / n:.0%}")
    print(f"Correctly rejected: {rj}/{m}")
    print("Tip: if off-topic questions score above MIN_SCORE, raise MIN_SCORE in .env; if good questions are rejected, lower it.")
