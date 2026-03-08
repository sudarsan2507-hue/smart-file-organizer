from ai.keyword_engine import KeywordEngine
from ai.embedding_engine import EmbeddingEngine


class HybridClassifier:

    def __init__(self):

        self.keyword_engine = KeywordEngine()
        self.embedding_engine = EmbeddingEngine()

        # minimum keyword score to trust keyword classification
        self.keyword_threshold = 2


    def classify(self, text):

        keyword_category, keyword_scores = self.keyword_engine.classify(text)

        keyword_score = keyword_scores[keyword_category]

        # If keyword match is strong enough, use it
        if keyword_score >= self.keyword_threshold:
            return {
                "method": "keyword",
                "category": keyword_category,
                "scores": keyword_scores
            }

        # Otherwise use AI embeddings
        embedding_category, embedding_scores = self.embedding_engine.classify(text)

        return {
            "method": "embedding",
            "category": embedding_category,
            "scores": embedding_scores
        }