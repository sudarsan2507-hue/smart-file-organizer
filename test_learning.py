"""
Test: User Feedback Learning System (Step 3)
==============================================
Creates temporary test files and verifies that the system
learns from manual corrections and boosts future classifications.
"""

import os
import shutil
import json
from core.pipeline import ProcessingPipeline
from core.learning_memory import LearningMemory

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
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "_test_learning_output"))
    clean_directory(test_dir)
    os.makedirs(test_dir, exist_ok=True)

    memory_path = os.path.join(test_dir, "learning_memory.json")
    
    # Instantiate pipeline with temporary dirs
    pipeline = ProcessingPipeline(
        base_directory=test_dir,
        confidence_threshold=0.65,
        learning_memory_path=memory_path
    )

    print("=" * 60)
    print("  User Feedback Learning System  -  Test Suite")
    print(f"  Confidence threshold: {pipeline.confidence_threshold}")
    print(f"  Memory Path: {memory_path}")
    print("=" * 60)

    # -------------------------------------------------------------
    # Test Case 1: Initial state before correction
    # -------------------------------------------------------------
    print("\n[STEP 1] Classifying a file containing 'research' keyword")
    file_content = "This document is about academic research."
    doc_path = create_test_file(test_dir, "paper1.txt", file_content)
    
    result1 = pipeline.process_file(doc_path)
    print(f"  Predicted Category: {result1['original_category']} (routed to {result1['category']})")
    print(f"  Confidence:         {result1['confidence']:.2f}")
    print(f"  Action Taken:       {result1['action']}")
    
    assert result1['original_category'] == 'Study', f"Expected 'Study', got '{result1['original_category']}'"
    print("  -> PASSED: Successfully predicted 'Study' initially.")

    # -------------------------------------------------------------
    # Test Case 2: Simulate User Manual Moves (Corrections)
    # -------------------------------------------------------------
    print("\n[STEP 2] Simulating user manual moves: Study -> Projects")
    
    corrections = [
        "This is research about machine learning.",
        "We are writing research implementation scripts.",
        "Academic research dataset training."
    ]
    
    memory = LearningMemory(filepath=memory_path)
    
    for i, content in enumerate(corrections):
        print(f"  Simulating correction {i+1}...")
        boosted = memory.record_correction(content, "Projects")
        print(f"    Extracted keywords: {boosted} -> boosted for 'Projects'")

    memory.load_memory()
    boosts = memory.get_boosts()
    print("\n[STEP 3] Verifying learning memory JSON content")
    print(json.dumps(boosts, indent=4))
    
    assert 'research' in boosts, "Expected 'research' keyword in boosts"
    assert boosts['research']['Projects'] == 3, f"Expected boost value 3, got {boosts['research']['Projects']}"
    print("  -> PASSED: Learning memory correctly recorded 3 manual moves.")

    # -------------------------------------------------------------
    # Test Case 3: Re-classify new file with boosted keyword
    # -------------------------------------------------------------
    print("\n[STEP 4] Classifying a new research document after learning")
    new_doc_content = "This is a new document about research and scripts."
    new_doc_path = create_test_file(test_dir, "paper_new.txt", new_doc_content)
    
    result2 = pipeline.process_file(new_doc_path)
    print(f"  Predicted Category: {result2['category']}")
    print(f"  Confidence:         {result2['confidence']:.2f}")
    print(f"  Action Taken:       {result2['action']}")
    
    assert result2['category'] == 'Projects', f"Expected 'Projects', got '{result2['category']}'"
    assert result2['action'] == 'auto_organized', f"Expected 'auto_organized', got '{result2['action']}'"
    print("  -> PASSED: Adaptive learning successfully boosted 'Projects' and auto-organized future files!")

    print("\n" + "=" * 60)
    print("  ALL 3 ADAPTIVE LEARNING TESTS PASSED SUCCESSFULLY! (SUCCESS)")
    print("=" * 60)

    # Cleanup
    print("\nCleaning up test directory...")
    clean_directory(test_dir)
    print("Done.")

if __name__ == "__main__":
    main()
