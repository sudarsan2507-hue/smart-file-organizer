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

    def _normalize(self, vector):
        vector = np.asarray(vector, dtype="float32")
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def add(self, filepath, filename, category, embedding):
        normalized = self._normalize(embedding).reshape(1, -1)
        self.index.add(normalized)
        self.metadata.append({
            "filepath": filepath,
            "filename": filename,
            "category": category,
        })
        self._save()

    def search(self, query_embedding, top_k=5):
        if self.index.ntotal == 0:
            return []

        normalized = self._normalize(query_embedding).reshape(1, -1)
        scores, indices = self.index.search(normalized, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            entry = self.metadata[idx]
            if not os.path.exists(entry["filepath"]):
                continue
            results.append({
                "filename": entry["filename"],
                "filepath": entry["filepath"],
                "category": entry["category"],
                "score": float(score),
            })

        return results[:top_k]

    def _save(self):
        os.makedirs(self.index_dir, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)
