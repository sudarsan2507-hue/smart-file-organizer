import sys
import os
import time
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.pipeline import ProcessingPipeline
from core.learning_memory import LearningMemory


def is_file_stable(filepath):
    initial_size = os.path.getsize(filepath)
    time.sleep(2)
    final_size = os.path.getsize(filepath)
    if initial_size == final_size:
        return True
    else:
        return False


class DownloadHandler(FileSystemEventHandler):

    # Ignore repeat corrections for the same file content within this window,
    # so accidentally dragging a file back and forth doesn't learn the same
    # correction multiple times.
    CORRECTION_COOLDOWN_SECONDS = 30

    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.base_dir = os.path.abspath(pipeline.organizer.base_directory)
        self._recent_corrections = {}  # content_hash -> last correction timestamp

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path

        # Ignore files created inside subdirectories (already organized files,
        # e.g. files the pipeline itself just moved into a category folder).
        parent_dir = os.path.abspath(os.path.dirname(file_path))
        if parent_dir != self.base_dir:
            return

        # Ignore temporary download files
        if file_path.endswith((".crdownload", ".tmp", ".part")):
            return

        print(f"New file detected: {file_path}")

        try:
            if is_file_stable(file_path):
                self.pipeline.process_file(file_path)
            else:
                print(f"File still downloading: {file_path}")

        except FileNotFoundError:
            print("File not ready yet...")

        except Exception as e:
            print(f"Error processing file: {e}")

    def on_moved(self, event):
        if event.is_directory:
            return

        src_path = os.path.abspath(event.src_path)
        dest_path = os.path.abspath(event.dest_path)

        src_dir = os.path.dirname(src_path)
        dest_dir = os.path.dirname(dest_path)

        # A user correction occurs only when a file is moved between two
        # different category folders inside the watched base directory.
        # A same-folder rename (src_dir == dest_dir) naturally falls through
        # because src_category would equal dest_category below.
        if (os.path.dirname(src_dir) == self.base_dir and
                os.path.dirname(dest_dir) == self.base_dir):

            src_category = os.path.basename(src_dir)
            dest_category = os.path.basename(dest_dir)

            if src_category != dest_category:
                filename = os.path.basename(dest_path)

                # Settle down to ensure file is readable
                time.sleep(0.5)

                try:
                    if os.path.exists(dest_path):
                        with open(dest_path, "r", encoding="utf-8", errors="ignore") as f:
                            text = f.read()

                        content_hash = hashlib.md5(
                            text.encode("utf-8", errors="ignore")
                        ).hexdigest()
                        now = time.time()
                        last_seen = self._recent_corrections.get(content_hash)
                        if last_seen is not None and (now - last_seen) < self.CORRECTION_COOLDOWN_SECONDS:
                            print(
                                f"[LEARNING] Skipping duplicate correction for '{filename}' "
                                f"(same content corrected within {self.CORRECTION_COOLDOWN_SECONDS}s)"
                            )
                            return
                        self._recent_corrections[content_hash] = now

                        # Retrieve configured learning memory path
                        learning_memory_path = getattr(
                            self.pipeline.classifier.keyword_engine,
                            "learning_memory_path",
                            None
                        )
                        memory = LearningMemory(filepath=learning_memory_path)
                        boosted_keywords = memory.record_correction(text, dest_category)

                        if boosted_keywords:
                            print(f"[LEARNING] User corrected prediction for '{filename}': {src_category} -> {dest_category}")
                            print(f"[LEARNING] Boosted weights for keywords: {boosted_keywords} -> '{dest_category}'")
                        else:
                            print(f"[LEARNING] User moved '{filename}' from {src_category} -> {dest_category}, but no matching keywords were found.")
                except Exception as e:
                    print(f"[LEARNING ERROR] Failed to record correction for '{filename}': {e}")


def process_existing_files(folder_path, pipeline):

    print("Scanning existing files...")

    for file in os.listdir(folder_path):

        file_path = os.path.join(folder_path, file)

        if os.path.isfile(file_path):

            print(f"Processing existing file: {file_path}")

            try:
                pipeline.process_file(file_path)

            except Exception as e:
                print(f"Error processing file: {e}")


def start_watching(folder_path):

    pipeline = ProcessingPipeline(folder_path)

    process_existing_files(folder_path, pipeline)

    event_handler = DownloadHandler(pipeline)

    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)

    observer.start()

    print(f"Watching folder: {folder_path}")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":

    downloads_path = r"D:\Download_chrome(P1)"

    start_watching(downloads_path)
