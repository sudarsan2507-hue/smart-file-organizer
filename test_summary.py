"""
Test: LLM Summary Engine (Phase 3.2)
======================================
Verifies that:
  1. SummaryEngine returns None gracefully when Ollama is not running.
  2. The pipeline still indexes files correctly when summary is None.
  3. When a summary is injected (mocked), it is stored and returned by search.
"""

import os
import shutil
from unittest.mock import patch

from ai.summary_engine import SummaryEngine
from core.pipeline import ProcessingPipeline


def clean_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def create_test_file(folder, name, content):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def main():
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "_test_summary_output"))
    clean_directory(test_dir)
    os.makedirs(test_dir, exist_ok=True)

    print("=" * 60)
    print("  LLM Summary Engine  -  Test Suite")
    print("=" * 60)

    # ---- Test 1: graceful fallback when Ollama is not running ----
    print("\n[TEST 1] SummaryEngine returns None when Ollama is unreachable")
    import urllib.error
    engine = SummaryEngine()
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("connection refused")):
        result = engine.summarize("This is a test document about machine learning and projects.")
    assert result is None, f"Expected None when Ollama is not running, got: {result!r}"
    print("  -> PASSED: summarize() returned None gracefully.")

    # ---- Test 2: pipeline indexes files even without a summary ----
    print("\n[TEST 2] Pipeline indexes files correctly when summary is None")
    pipeline = ProcessingPipeline(base_directory=test_dir)

    doc_path = create_test_file(
        test_dir, "report.txt",
        "This github repository contains machine learning model training scripts and dataset."
    )
    with patch.object(pipeline.summary_engine, "summarize", return_value=None):
        result = pipeline.process_file(doc_path)
    assert result["category"] != "", "Expected a non-empty category"

    dest = os.path.join(test_dir, result["category"], "report.txt")
    entry = pipeline.semantic_index.metadata[
        pipeline.semantic_index._filepath_to_id[dest]
    ]
    assert entry.get("word_count", 0) > 0, "Expected word_count to be set"
    assert "summary" not in entry, "Expected no summary key when Ollama is unavailable"
    print(f"  -> PASSED: indexed as '{result['category']}' with no summary key.")

    # ---- Test 3: mocked summary is stored and returned by search ----
    print("\n[TEST 3] Mocked summary is stored in index and returned by search")

    clean_directory(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    pipeline2 = ProcessingPipeline(base_directory=test_dir)

    fake_summary = "A machine learning project with training scripts and dataset preparation."

    doc2_path = create_test_file(
        test_dir, "project_notes.txt",
        "This github repository contains machine learning model training scripts and dataset."
    )

    with patch.object(pipeline2.summary_engine, "summarize", return_value=fake_summary):
        result2 = pipeline2.process_file(doc2_path)

    dest2 = os.path.join(test_dir, result2["category"], "project_notes.txt")
    entry2 = pipeline2.semantic_index.metadata[
        pipeline2.semantic_index._filepath_to_id[dest2]
    ]
    assert entry2.get("summary") == fake_summary, (
        f"Expected summary in index, got: {entry2.get('summary')!r}"
    )

    search_results = pipeline2.semantic_index.search(
        pipeline2.classifier.embedding_engine.embed_text("machine learning project"),
        top_k=1
    )
    assert len(search_results) > 0, "Expected at least one search result"
    assert search_results[0].get("summary") == fake_summary, (
        f"Expected summary in search result, got: {search_results[0].get('summary')!r}"
    )
    print(f"  -> PASSED: summary stored and returned by search.")
    print(f"     summary: {fake_summary}")

    print("\n" + "=" * 60)
    print("  ALL SUMMARY TESTS PASSED SUCCESSFULLY! (SUCCESS)")
    print("=" * 60)

    print("\nCleaning up test directory...")
    clean_directory(test_dir)
    print("Done.")


if __name__ == "__main__":
    main()
