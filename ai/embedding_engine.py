from sentence_transformers import SentenceTransformer
import numpy as np
from config.categories import CATEGORIES


class EmbeddingEngine:

    def __init__(self):
        # Load model ONLY ONCE
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Prepare category descriptions
        self.category_texts = {}

        for category, keywords in CATEGORIES.items():
            self.category_texts[category] = " ".join(keywords)

        # Convert category descriptions to embeddings
        self.category_embeddings = {}

        for category, text in self.category_texts.items():
            self.category_embeddings[category] = self.model.encode(text)


    def cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


    def classify(self, text):

        # Convert file text to embedding
        text_embedding = self.model.encode(text)

        scores = {}

        for category, category_embedding in self.category_embeddings.items():

            similarity = self.cosine_similarity(text_embedding, category_embedding)

            scores[category] = float(similarity)

        best_category = max(scores, key=scores.get)

        return best_category, scores