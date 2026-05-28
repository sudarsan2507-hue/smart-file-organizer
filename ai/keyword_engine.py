from config.categories import CATEGORIES


class KeywordEngine:

    def classify(self, text):

        text = text.lower()

        scores = {}

        for category, keywords in CATEGORIES.items():

            score = 0

            for keyword in keywords:
                if keyword in text:
                    score += 1

            scores[category] = score

        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]
        total_keywords_found = sum(scores.values())

        confidence = (best_score / total_keywords_found) if total_keywords_found > 0 else 0.0

        return best_category, confidence, scores