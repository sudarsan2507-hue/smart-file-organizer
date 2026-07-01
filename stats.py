import os
import json
import argparse
from collections import Counter


def main():
    parser = argparse.ArgumentParser(description="Show statistics for organized files")
    parser.add_argument("base_directory", help="The folder managed by the watcher/pipeline")
    args = parser.parse_args()

    meta_path = os.path.join(args.base_directory, ".semantic_index", "meta.json")
    if not os.path.exists(meta_path):
        print("No index found. Run the watcher or pipeline first.")
        return

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    active = [e for e in metadata if os.path.exists(e["filepath"])]
    stale = len(metadata) - len(active)

    categories = Counter(e["category"] for e in active)
    languages = Counter(e.get("language") or "unknown" for e in active)
    tag_counter = Counter()
    for e in active:
        for tag in e.get("tags") or []:
            tag_counter[tag] += 1
    total_words = sum(e.get("word_count") or 0 for e in active)
    with_summary = sum(1 for e in active if e.get("summary"))

    W = 50
    print(f"\n{'='*W}")
    print(f"  Document Statistics")
    print(f"{'='*W}")
    print(f"  Total indexed : {len(active)}")
    if stale:
        print(f"  Stale entries : {stale}  (file no longer exists)")
    print(f"  Total words   : {total_words:,}")
    print(f"  With summary  : {with_summary}")

    print(f"\n  Files by category:")
    for cat, count in categories.most_common():
        bar = "#" * count
        print(f"    {cat:<15} {count:>4}  {bar}")

    print(f"\n  Languages:")
    for lang, count in languages.most_common():
        print(f"    {lang:<15} {count}")

    if tag_counter:
        print(f"\n  Top 10 tags:")
        for tag, count in tag_counter.most_common(10):
            print(f"    {tag:<22} {count}")

    print(f"{'='*W}\n")


if __name__ == "__main__":
    main()
