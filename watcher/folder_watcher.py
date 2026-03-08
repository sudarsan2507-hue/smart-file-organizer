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

    # Process files already in folder
    process_existing_files(folder_path, pipeline)

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


if __name__ == "__main__":

    downloads_path = r"D:\Download_chrome(P1)"

    start_watching(downloads_path)