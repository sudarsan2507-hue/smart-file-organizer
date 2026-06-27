import os

from ai.content_reader import ContentReader
from ai.hybrid_classifier import HybridClassifier
from core.organizer import FileOrganizer


EXTENSION_MAP = {
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
    ".gif": "Images", ".webp": "Images", ".bmp": "Images",
    ".svg": "Images", ".ico": "Images",
    # Videos
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos",
    ".mov": "Videos", ".wmv": "Videos", ".flv": "Videos",
    # Audio
    ".mp3": "Audio", ".wav": "Audio", ".aac": "Audio",
    ".flac": "Audio", ".ogg": "Audio", ".wma": "Audio",
    # Archives
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives",
    ".tar": "Archives", ".gz": "Archives",
}


class ProcessingPipeline:

    DEFAULT_CONFIDENCE_THRESHOLD = 0.65

    def __init__(self, base_directory, confidence_threshold=None, learning_memory_path=None):

        self.reader = ContentReader()
        self.classifier = HybridClassifier(learning_memory_path=learning_memory_path)
        self.organizer = FileOrganizer(base_directory)

        self.confidence_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else self.DEFAULT_CONFIDENCE_THRESHOLD
        )

    def process_file(self, file_path):

        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        # -------- 1. EXTENSION-BASED (deterministic) --------

        if ext in EXTENSION_MAP:
            category = EXTENSION_MAP[ext]
            confidence = 1.0
            method = "extension"

            print(f"[EXTENSION]  {filename} -> {category}")

            self.organizer.organize(file_path, category)

            return {
                "filename": filename,
                "category": category,
                "confidence": confidence,
                "method": method,
                "action": "auto_organized",
            }

        # -------- 2. CONTENT-BASED (AI classification) --------

        text = self.reader.read_file(file_path)

        if not text.strip():
            category = "Others"
            confidence = 0.0
            method = "empty"

            print(f"[EMPTY]  {filename} -> Others (no readable content)")

            self.organizer.organize(file_path, category)

            return {
                "filename": filename,
                "category": category,
                "confidence": confidence,
                "method": method,
                "action": "auto_organized",
            }

        result = self.classifier.classify(text)
        category = result["category"]
        confidence = result["confidence"]
        method = result["method"]

        # -------- 3. CONFIDENCE DECISION --------

        final_category, action = self._apply_confidence_decision(
            filename, category, confidence, method
        )

        # -------- 4. MOVE FILE --------

        self.organizer.organize(file_path, final_category)

        return {
            "filename": filename,
            "category": final_category,
            "original_category": category,
            "confidence": confidence,
            "method": method,
            "action": action,
        }

    def _apply_confidence_decision(self, filename, category, confidence, method):
        """
        High confidence  ->  auto-organize into predicted category
        Low  confidence  ->  route to Review folder for human inspection
        """

        tag = method.upper()

        if confidence >= self.confidence_threshold:
            print(
                f"[{tag}]  {filename} -> {category} "
                f"({confidence:.2f} >= {self.confidence_threshold})"
            )
            return category, "auto_organized"

        else:
            print(
                f"[LOW CONFIDENCE]  {filename} -> Review "
                f"(predicted {category} @ {confidence:.2f} "
                f"< threshold {self.confidence_threshold})"
            )
            return "Review", "needs_review"
