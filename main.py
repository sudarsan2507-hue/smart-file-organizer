"""
Unified entry point for the local AI document management platform.

Commands:
  watch     Watch a folder and auto-organize new files
  search    Semantic search over organized files
  similar   Find documents similar to a given file
  stats     Show statistics for the organized collection
  reindex   Rebuild the semantic index from scratch
"""

import sys
import argparse


def cmd_watch(args):
    from watcher.folder_watcher import start_watching
    start_watching(args.folder)


def cmd_search(args):
    import os
    from ai.embedding_engine import EmbeddingEngine
    from core.semantic_index import SemanticIndex
    from search import print_results

    index_dir = os.path.join(args.folder, ".semantic_index")
    print("Loading embedding model...")
    engine = EmbeddingEngine()
    index = SemanticIndex(dim=engine.model.get_sentence_embedding_dimension(), index_dir=index_dir)
    query_embedding = engine.embed_text(args.query)
    results = index.search(query_embedding, top_k=args.top_k)
    print_results(results, f"Top {len(results)} result(s) for: \"{args.query}\"")


def cmd_similar(args):
    import os
    from ai.embedding_engine import EmbeddingEngine
    from core.semantic_index import SemanticIndex
    from search import print_results

    index_dir = os.path.join(args.folder, ".semantic_index")
    print("Loading embedding model...")
    engine = EmbeddingEngine()
    index = SemanticIndex(dim=engine.model.get_sentence_embedding_dimension(), index_dir=index_dir)
    filepath = os.path.abspath(args.filepath)
    results = index.find_similar(filepath, top_k=args.top_k)
    print_results(results, f"Top {len(results)} document(s) similar to: \"{filepath}\"")


def cmd_stats(args):
    import stats as stats_module
    sys.argv = ["stats", args.folder]
    stats_module.main()


def cmd_reindex(args):
    import reindex as reindex_module
    argv = ["reindex", args.folder]
    if args.with_summaries:
        argv.append("--with-summaries")
    sys.argv = argv
    reindex_module.main()


def main():
    parser = argparse.ArgumentParser(
        description="Local AI document management platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = True

    # watch
    p_watch = sub.add_parser("watch", help="Watch a folder and auto-organize files")
    p_watch.add_argument("folder", help="Folder to watch")
    p_watch.set_defaults(func=cmd_watch)

    # search
    p_search = sub.add_parser("search", help="Semantic search over organized files")
    p_search.add_argument("folder", help="Organized folder")
    p_search.add_argument("query", help="Natural language query")
    p_search.add_argument("--top-k", type=int, default=5)
    p_search.set_defaults(func=cmd_search)

    # similar
    p_similar = sub.add_parser("similar", help="Find documents similar to a given file")
    p_similar.add_argument("folder", help="Organized folder")
    p_similar.add_argument("filepath", help="Path to an already-organized file")
    p_similar.add_argument("--top-k", type=int, default=5)
    p_similar.set_defaults(func=cmd_similar)

    # stats
    p_stats = sub.add_parser("stats", help="Show statistics for the organized collection")
    p_stats.add_argument("folder", help="Organized folder")
    p_stats.set_defaults(func=cmd_stats)

    # reindex
    p_reindex = sub.add_parser("reindex", help="Rebuild the semantic index from organized files")
    p_reindex.add_argument("folder", help="Organized folder")
    p_reindex.add_argument("--with-summaries", action="store_true",
                           help="Generate summaries via Ollama (requires Ollama to be running)")
    p_reindex.set_defaults(func=cmd_reindex)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
