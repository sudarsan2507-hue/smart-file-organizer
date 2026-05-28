import os
import json
from config.categories import CATEGORIES

class LearningMemory:
    def __init__(self, filepath=None):
        if filepath is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.filepath = os.path.join(base_dir, "learning_memory.json")
        else:
            self.filepath = filepath
        self.memory = {}
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
            except Exception as e:
                print(f"[LEARNING ERROR] Failed to load learning memory: {e}")
                self.memory = {}
        else:
            self.memory = {}

        if "keyword_boosts" not in self.memory:
            self.memory["keyword_boosts"] = {}

    def save_memory(self):
        try:
            dir_name = os.path.dirname(self.filepath)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"[LEARNING ERROR] Failed to save learning memory: {e}")

    def record_correction(self, text, target_category):
        """
        Scan text for keywords in config categories, and increment association with target_category.
        """
        text = text.lower()
        boosted_keywords = []

        for category, keywords in CATEGORIES.items():
            for keyword in keywords:
                if keyword in text:
                    if keyword not in self.memory["keyword_boosts"]:
                        self.memory["keyword_boosts"][keyword] = {}

                    current_boost = self.memory["keyword_boosts"][keyword].get(target_category, 0)
                    self.memory["keyword_boosts"][keyword][target_category] = current_boost + 1
                    boosted_keywords.append(keyword)

        if boosted_keywords:
            self.save_memory()
        return list(set(boosted_keywords))

    def get_boosts(self):
        return self.memory.get("keyword_boosts", {})
