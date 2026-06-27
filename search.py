import sys
import os
import argparse

from ai.embedding_engine import EmbeddingEngine
from core.semantic_index import SemanticIndex


def main():
    parser = argparse.ArgumentParser(description="Semantic search over organized files")
    parser.add_argument("query", help="Natural language query, e.g. 'my internship offer letter'")
    parser.add_argument("base_directory", help="The folder previously organized by the watcher/pipeline")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to show")
    args = parser.parse_args()

    index_dir = os.path.join(args.base_directory, ".semantic_index")

    print("Loading embedding model...")
    engine = EmbeddingEngine()

    index = SemanticIndex(dim=engine.model.get_sentence_embedding_dimension(), index_dir=index_dir)

    query_embedding = engine.embed_text(args.query)
    results = index.search(query_embedding, top_k=args.top_k)

    if not results:
        print("No indexed documents matched (or nothing has been indexed yet).")
        return

    print(f"\nTop {len(results)} result(s) for: \"{args.query}\"\n")
    for rank, result in enumerate(results, start=1):
        print(f"{rank}. {result['filename']}  [{result['category']}]  score={result['score']:.3f}")
        print(f"   {result['filepath']}")


if __name__ == "__main__":
    main()
