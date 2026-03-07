import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from classifier import get_file_category
from organizer import move_file

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
                category = get_file_category(file_path)
                print(f"Category: {category}")
                move_file(file_path, category)
            else:
                print(f"File still downloading: {file_path}")

        except FileNotFoundError:
            print("File not ready yet...")
def organize_existing_files(folder_path):

    print("Scanning existing files...")

    for file in os.listdir(folder_path):

        file_path = os.path.join(folder_path, file)

        if os.path.isdir(file_path):
            continue

        if file_path.endswith((".crdownload", ".tmp", ".part")):
            continue

        try:
            category = get_file_category(file_path)
            move_file(file_path, category)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":

    path_to_watch = r"D:\Download_chrome(stu)"
    organize_existing_files(path_to_watch)

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