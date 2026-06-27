from config.categories import CATEGORIES
from core.learning_memory import LearningMemory

# Cap on how much a single learned keyword->category boost can contribute to
# a category's score, so one repeatedly-corrected keyword can't permanently
# dominate a category no matter how many times it accumulates.
MAX_BOOST = 5


class KeywordEngine:

    def __init__(self, learning_memory_path=None):
        self.learning_memory_path = learning_memory_path

    def classify(self, text):

        text = text.lower()

        scores = {}

        # Load dynamic boosts from user feedback
        memory = LearningMemory(filepath=self.learning_memory_path)
        boosts = memory.get_boosts()

        for category, keywords in CATEGORIES.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text:
                    score += 1.0
            scores[category] = score

        # Apply learned boosts from user manual corrections directly into the
        # scores, capped per keyword/category so confidence stays derived
        # purely from the (now boosted) scores rather than added on top.
        for category in CATEGORIES.keys():
            for keyword, category_boosts in boosts.items():
                if keyword in text:
                    boost = category_boosts.get(category, 0)
                    if boost > 0:
                        scores[category] += float(min(boost, MAX_BOOST))

        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]

        # Confidence is the winner's margin over the runner-up, derived
        # purely from `scores` (native matches + learned boosts already
        # folded in above) — learning influences confidence only by
        # widening that margin, never through a separate additive bonus.
        # A total-score-share formula was considered, but it dilutes
        # confidence as unrelated categories are added to CATEGORIES and
        # systematically under-rewards learned boosts, since a boosted
        # keyword by definition isn't in its target category's native list.
        sorted_scores = sorted(scores.values(), reverse=True)
        second_best = sorted_scores[1] if len(sorted_scores) > 1 else 0.0
        confidence = ((best_score - second_best) / best_score) if best_score > 0 else 0.0

        return best_category, confidence, scores