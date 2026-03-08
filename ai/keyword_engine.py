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

        return best_category, scores