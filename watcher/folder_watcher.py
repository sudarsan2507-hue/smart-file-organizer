import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def is_file_stable(filepath):

    initial_size = os.path.getsize(filepath)

    time.sleep(2)

    final_size = os.path.getsize(filepath)

    if initial_size == final_size:
        return True
    else:
        return False


class DownloadHandler(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        file_path = event.src_path

        # Ignore temporary download files
        if file_path.endswith((".crdownload", ".tmp", ".part")):
            return

        print(f"File detected: {file_path}")

        try:
            if is_file_stable(file_path):
                print(f"File is stable and ready: {file_path}")
            else:
                print(f"File still downloading: {file_path}")

        except FileNotFoundError:
            print("File not ready yet...")

if __name__ == "__main__":

    path_to_watch = r"D:\Download_chrome(P1)"

    event_handler = DownloadHandler()

    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)

    observer.start()

    print("Watching folder for new files...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()