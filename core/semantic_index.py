import os
import json

import numpy as np
import faiss


class SemanticIndex:

    def __init__(self, dim, index_dir=None):
        self.dim = dim
        self.index_dir = index_dir
        self.index_path = os.path.join(index_dir, "index.faiss")
        self.meta_path = os.path.join(index_dir, "meta.json")

        self.metadata = []

        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(dim)

        self._filepath_to_id = {
            entry["filepath"]: idx for idx, entry in enumerate(self.metadata)
        }

    def _normalize(self, vector):
        vector = np.asarray(vector, dtype="float32")
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def add(self, filepath, filename, category, embedding, extra_metadata=None):
        normalized = self._normalize(embedding).reshape(1, -1)
        self.index.add(normalized)

        entry = {
            "filepath": filepath,
            "filename": filename,
            "category": category,
        }
        if extra_metadata:
            entry.update(extra_metadata)

        self._filepath_to_id[filepath] = len(self.metadata)
        self.metadata.append(entry)
        self._save()

    def _entry_to_result(self, entry, score):
        return {
            "filename": entry["filename"],
            "filepath": entry["filepath"],
            "category": entry["category"],
            "score": float(score),
            "word_count": entry.get("word_count"),
            "language": entry.get("language"),
            "tags": entry.get("tags", []),
            "created_date": entry.get("created_date"),
            "modified_date": entry.get("modified_date"),
        }

    def search(self, query_embedding, top_k=5, exclude_filepath=None):
        if self.index.ntotal == 0:
            return []

        normalized = self._normalize(query_embedding).reshape(1, -1)
        fetch_k = min(top_k + (1 if exclude_filepath else 0), self.index.ntotal)
        scores, indices = self.index.search(normalized, fetch_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            entry = self.metadata[idx]
            if entry["filepath"] == exclude_filepath:
                continue
            if not os.path.exists(entry["filepath"]):
                continue
            results.append(self._entry_to_result(entry, score))

        return results[:top_k]

    def find_similar(self, filepath, top_k=5):
        row_id = self._filepath_to_id.get(filepath)
        if row_id is None:
            return []

        embedding = self.index.reconstruct(row_id)
        return self.search(embedding, top_k=top_k, exclude_filepath=filepath)

    def _save(self):
        os.makedirs(self.index_dir, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)
