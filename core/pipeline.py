import os

from ai.content_reader import ContentReader
from ai.hybrid_classifier import HybridClassifier
from core.organizer import FileOrganizer


class ProcessingPipeline:

    def __init__(self, base_directory):

        self.reader = ContentReader()
        self.classifier = HybridClassifier()
        self.organizer = FileOrganizer(base_directory)


    def process_file(self, file_path):

        filename = os.path.basename(file_path).lower()
        ext = os.path.splitext(filename)[1]

        # -------- EXTENSION BASED CLASSIFICATION --------

        image_ext = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        video_ext = [".mp4", ".mkv", ".avi", ".mov"]
        audio_ext = [".mp3", ".wav", ".aac", ".flac"]
        archive_ext = [".zip", ".rar", ".7z"]
        document_ext = [".pdf", ".docx", ".txt"]

        if ext in image_ext:
            category = "Images"

        elif ext in video_ext:
            category = "Videos"

        elif ext in audio_ext:
            category = "Audio"

        elif ext in archive_ext:
            category = "Archives"

        else:

            # -------- CONTENT BASED CLASSIFICATION --------

            text = self.reader.read_file(file_path)

            if not text.strip():
                category = "Others"

            else:
                result = self.classifier.classify(text)
                category = result["category"]

        print(f"{filename} -> {category}")

        # -------- MOVE FILE --------

        self.organizer.organize(file_path, category)

        return category