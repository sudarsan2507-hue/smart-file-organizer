import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.pipeline import ProcessingPipeline

class DownloadHandler(FileSystemEventHandler):

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def on_created(self, event):

        if event.is_directory:
            return

        file_path = event.src_path

        print(f"New file detected: {file_path}")

        try:
            self.pipeline.process_file(file_path)

        except Exception as e:
            print(f"Error processing file: {e}")


def start_watching(folder_path):

    pipeline = ProcessingPipeline(folder_path)

    event_handler = DownloadHandler(pipeline)

    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)

    observer.start()

    print(f"Watching folder: {folder_path}")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()