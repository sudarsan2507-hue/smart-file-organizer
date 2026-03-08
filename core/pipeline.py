from ai.content_reader import ContentReader
from ai.hybrid_classifier import HybridClassifier
from core.organizer import FileOrganizer


class ProcessingPipeline:

    def __init__(self, base_directory):

        self.reader = ContentReader()
        self.classifier = HybridClassifier()
        self.organizer = FileOrganizer(base_directory)


    def process_file(self, file_path):

        text = self.reader.read_file(file_path)

        if not text.strip():
            category = "Others"
        else:
            result = self.classifier.classify(text)
            category = result["category"]

        self.organizer.organize(file_path, category)

        return category