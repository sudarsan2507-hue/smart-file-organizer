from ai.keyword_engine import KeywordEngine
from ai.embedding_engine import EmbeddingEngine


class HybridClassifier:

    def __init__(self, learning_memory_path=None):

        self.keyword_engine = KeywordEngine(learning_memory_path=learning_memory_path)
        self.embedding_engine = EmbeddingEngine()

        # minimum keyword score to trust keyword classification
        self.keyword_threshold = 2


    def classify(self, text):

        keyword_category, keyword_confidence, keyword_scores = self.keyword_engine.classify(text)
        keyword_score = keyword_scores[keyword_category]

        # If keyword match is strong enough, use it
        if keyword_score >= self.keyword_threshold:
            return {
                "method": "keyword",
                "category": keyword_category,
                "confidence": keyword_confidence,
                "scores": keyword_scores
            }

        # Otherwise use AI embeddings
        embedding_category, embedding_confidence, embedding_scores = self.embedding_engine.classify(text)

        return {
            "method": "embedding",
            "category": embedding_category,
            "confidence": embedding_confidence,
            "scores": embedding_scores
        }
