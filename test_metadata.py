"""
Test: Document Metadata, Tags, and Similar Documents (Phase 3.1)
==================================================================
Processes a few documents and verifies that word count / language / tags
are populated, and that find_similar() ranks a topically related document
above an unrelated one.
"""

import os
import shutil
from core.pipeline import ProcessingPipeline

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
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "_test_metadata_output"))
    clean_directory(test_dir)
    os.makedirs(test_dir, exist_ok=True)

    pipeline = ProcessingPipeline(base_directory=test_dir)

    print("=" * 60)
    print("  Metadata / Tags / Similar Documents  -  Test Suite")
    print("=" * 60)

    print("\n[STEP 1] Processing documents")
    project_a_path = create_test_file(
        test_dir, "project_a.txt",
        "This github repository contains the implementation and training "
        "scripts for our machine learning model and dataset."
    )
    project_b_path = create_test_file(
        test_dir, "project_b.txt",
        "Another github project repository with model training "
        "implementation and dataset preparation scripts."
    )
    invoice_path = create_test_file(
        test_dir, "invoice1.txt",
        "Invoice for payment of tax and salary, please settle the balance amount."
    )

    result_a = pipeline.process_file(project_a_path)
    result_b = pipeline.process_file(project_b_path)
    result_invoice = pipeline.process_file(invoice_path)

    print(f"  '{result_a['filename']}' -> {result_a['category']}")
    print(f"  '{result_b['filename']}' -> {result_b['category']}")
    print(f"  '{result_invoice['filename']}' -> {result_invoice['category']}")

    print("\n[STEP 2] Verifying metadata fields")
    entry_a = pipeline.semantic_index.metadata[
        pipeline.semantic_index._filepath_to_id[
            os.path.join(test_dir, result_a['category'], "project_a.txt")
        ]
    ]
    print(f"  word_count={entry_a['word_count']}  language={entry_a['language']}  tags={entry_a['tags']}")

    assert entry_a["word_count"] > 0, "Expected a positive word count"
    assert entry_a["language"] != "", "Expected a non-empty language code"
    assert len(entry_a["tags"]) > 0, "Expected at least one tag for a keyword-rich document"
    assert "github" in entry_a["tags"], f"Expected 'github' in tags, got {entry_a['tags']}"
    print("  -> PASSED: Metadata fields populated as expected.")

    print("\n[STEP 3] Finding documents similar to project_a.txt")
    project_a_dest = os.path.join(test_dir, result_a['category'], "project_a.txt")
    similar = pipeline.semantic_index.find_similar(project_a_dest, top_k=2)

    for r in similar:
        print(f"    {r['filename']}  score={r['score']:.3f}")

    assert len(similar) > 0, "Expected at least one similar document"
    assert similar[0]["filename"] == "project_b.txt", (
        f"Expected 'project_b.txt' as the most similar document, got '{similar[0]['filename']}'"
    )
    assert all(r["filename"] != "project_a.txt" for r in similar), (
        "find_similar() should not return the query document itself"
    )
    print("  -> PASSED: project_b.txt ranked as most similar to project_a.txt, self excluded.")

    print("\n" + "=" * 60)
    print("  ALL METADATA TESTS PASSED SUCCESSFULLY! (SUCCESS)")
    print("=" * 60)

    print("\nCleaning up test directory...")
    clean_directory(test_dir)
    print("Done.")

if __name__ == "__main__":
    main()
