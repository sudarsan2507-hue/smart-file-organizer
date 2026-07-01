import os
import argparse

from ai.embedding_engine import EmbeddingEngine
from core.semantic_index import SemanticIndex


def print_results(results, heading):
    if not results:
        print("No indexed documents matched (or nothing has been indexed yet).")
        return

    print(f"\n{heading}\n")
    for rank, result in enumerate(results, start=1):
        tags = ", ".join(result.get("tags") or [])
        print(f"{rank}. {result['filename']}  [{result['category']}]  score={result['score']:.3f}")
        print(f"   {result['filepath']}")
        print(f"   words={result.get('word_count')}  lang={result.get('language')}  tags=[{tags}]")
        if result.get("summary"):
            print(f"   summary: {result['summary']}")


def main():
    parser = argparse.ArgumentParser(description="Semantic search over organized files")
    parser.add_argument("base_directory", help="The folder previously organized by the watcher/pipeline")
    parser.add_argument("query", nargs="?", help="Natural language query, e.g. 'my internship offer letter'")
    parser.add_argument("--similar-to", metavar="FILEPATH",
                         help="Find documents similar to an already-organized file, instead of a text query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to show")
    args = parser.parse_args()

    if not args.query and not args.similar_to:
        parser.error("provide either a query or --similar-to")

    index_dir = os.path.join(args.base_directory, ".semantic_index")

    print("Loading embedding model...")
    engine = EmbeddingEngine()

    index = SemanticIndex(dim=engine.model.get_sentence_embedding_dimension(), index_dir=index_dir)

    if args.similar_to:
        filepath = os.path.abspath(args.similar_to)
        results = index.find_similar(filepath, top_k=args.top_k)
        print_results(results, f"Top {len(results)} document(s) similar to: \"{filepath}\"")
    else:
        query_embedding = engine.embed_text(args.query)
        results = index.search(query_embedding, top_k=args.top_k)
        print_results(results, f"Top {len(results)} result(s) for: \"{args.query}\"")


if __name__ == "__main__":
    main()
