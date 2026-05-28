from ai.content_reader import ContentReader
from ai.hybrid_classifier import HybridClassifier

reader = ContentReader()
classifier = HybridClassifier()

text = reader.read_file("test.txt")

result = classifier.classify(text)

print("Method Used:", result["method"])
print("Detected Category:", result["category"])
print("Confidence:", result["confidence"])
print("Scores:", result["scores"])