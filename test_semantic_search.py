"""
Test: Semantic Search over Organized Files (Phase 2)
======================================================
Creates a few topically distinct test files, runs them through the
pipeline, and verifies that a natural-language query retrieves the
relevant file via the persisted embedding index.
"""

import os
import shutil
from core.pipeline import ProcessingPipeline
from ai.embedding_engine import EmbeddingEngine

def clean_directory(path):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"Cleanup error for {path}: {e}")

def create_test_file(folder, name, content):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def main():
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "_test_semantic_search_output"))
    clean_directory(test_dir)
    os.makedirs(test_dir, exist_ok=True)

    pipeline = ProcessingPipeline(base_directory=test_dir)

    print("=" * 60)
    print("  Semantic Search  -  Test Suite")
    print("=" * 60)

    print("\n[STEP 1] Processing topically distinct documents")
    internship_path = create_test_file(
        test_dir, "letter1.txt",
        "This is an internship completion letter confirming the student "
        "successfully finished their internship at the company."
    )
    finance_path = create_test_file(
        test_dir, "invoice1.txt",
        "Invoice for payment of tax and salary, please settle the balance amount."
    )

    result1 = pipeline.process_file(internship_path)
    result2 = pipeline.process_file(finance_path)

    print(f"  '{result1['filename']}' -> {result1['category']}")
    print(f"  '{result2['filename']}' -> {result2['category']}")

    print("\n[STEP 2] Querying the semantic index")
    query = "internship completion letter"
    engine = EmbeddingEngine()
    query_embedding = engine.embed_text(query)

    results = pipeline.semantic_index.search(query_embedding, top_k=2)
    print(f"  Query: \"{query}\"")
    for r in results:
        print(f"    {r['filename']}  score={r['score']:.3f}")

    assert len(results) > 0, "Expected at least one search result"
    assert results[0]["filename"] == "letter1.txt", (
        f"Expected top result 'letter1.txt', got '{results[0]['filename']}'"
    )
    print("  -> PASSED: Internship letter ranked first for a matching query.")

    print("\n" + "=" * 60)
    print("  ALL SEMANTIC SEARCH TESTS PASSED SUCCESSFULLY! (SUCCESS)")
    print("=" * 60)

    print("\nCleaning up test directory...")
    clean_directory(test_dir)
    print("Done.")

if __name__ == "__main__":
    main()
