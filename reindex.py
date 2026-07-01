"""
Rebuild the semantic index from scratch by re-scanning all organized files.

Use this when:
  - The index file is corrupted or missing
  - You want to add summaries after enabling Ollama
  - You changed the embedding model
  - You added files manually without the watcher running
"""

import os
import argparse
import shutil

from ai.content_reader import ContentReader
from ai.embedding_engine import EmbeddingEngine
from ai.metadata_extractor import extract_metadata
from ai.summary_engine import SummaryEngine
from core.semantic_index import SemanticIndex
from config.categories import CATEGORIES

KNOWN_CATEGORIES = set(CATEGORIES.keys()) | {
    "Images", "Videos", "Audio", "Archives", "Others", "Review"
}


def main():
    parser = argparse.ArgumentParser(description="Rebuild the semantic index from organized files")
    parser.add_argument("base_directory", help="The folder managed by the watcher/pipeline")
    parser.add_argument("--with-summaries", action="store_true",
                        help="Generate summaries via Ollama (requires Ollama to be running)")
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_directory)
    index_dir = os.path.join(base_dir, ".semantic_index")

    print("Loading models...")
    reader = ContentReader()
    engine = EmbeddingEngine()
    summary_engine = SummaryEngine() if args.with_summaries else None
    dim = engine.model.get_sentence_embedding_dimension()

    # Wipe and recreate the index
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)
    index = SemanticIndex(dim=dim, index_dir=index_dir)

    total = 0
    skipped = 0

    for category in os.listdir(base_dir):
        category_path = os.path.join(base_dir, category)
        if not os.path.isdir(category_path):
            continue
        if category.startswith("."):
            continue
        if category not in KNOWN_CATEGORIES:
            continue

        for filename in os.listdir(category_path):
            filepath = os.path.join(category_path, filename)
            if not os.path.isfile(filepath):
                continue

            text = reader.read_file(filepath)
            if not text.strip():
                skipped += 1
                print(f"  [SKIP] {filename}  (no readable content)")
                continue

            embedding = engine.embed_text(text)
            metadata = extract_metadata(text, filepath, category)

            if summary_engine:
                summary = summary_engine.summarize(text)
                if summary:
                    metadata["summary"] = summary

            index.add(filepath, filename, category, embedding, extra_metadata=metadata)
            total += 1
            print(f"  [INDEXED] {category}/{filename}")

    print(f"\nDone. {total} file(s) indexed, {skipped} skipped.")


if __name__ == "__main__":
    main()
