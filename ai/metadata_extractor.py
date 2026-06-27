import os
from datetime import datetime

from langdetect import detect, LangDetectException

from config.categories import CATEGORIES

MAX_TAGS = 8


def _detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def _extract_tags(text):
    text = text.lower()
    counts = {}

    for keywords in CATEGORIES.values():
        for keyword in keywords:
            occurrences = text.count(keyword)
            if occurrences > 0:
                counts[keyword] = counts.get(keyword, 0) + occurrences

    ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    return [keyword for keyword, _ in ranked[:MAX_TAGS]]


def extract_metadata(text, filepath, category):
    created_date = datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
    modified_date = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()

    return {
        "word_count": len(text.split()),
        "language": _detect_language(text),
        "created_date": created_date,
        "modified_date": modified_date,
        "tags": _extract_tags(text),
    }
