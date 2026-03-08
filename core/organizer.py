import os
import shutil
import time


class FileOrganizer:

    def __init__(self, base_directory):

        self.base_directory = base_directory

        self.categories = {
            "Images": "Images",
            "Videos": "Videos",
            "Archives": "Archives",
            "Documents": "Documents",
            "Finance": "Finance",
            "Study": "Study",
            "Projects": "Projects",
            "Resume": "Resume",
            "Personal": "Personal",
            "Audio": "Audio",
            "Others": "Others"
        }


    def organize(self, file_path, category):

        # Get folder name
        folder = self.categories.get(category, "Others")

        # Create destination folder
        destination_folder = os.path.join(self.base_directory, folder)
        os.makedirs(destination_folder, exist_ok=True)

        filename = os.path.basename(file_path)
        destination = os.path.join(destination_folder, filename)

        # Prevent moving if already in correct folder
        if os.path.dirname(file_path) == destination_folder:
            return

        # Wait for file to be released (important for downloads)
        for attempt in range(10):

            try:
                shutil.move(file_path, destination)
                print(f"Moved {filename} -> {folder}")
                return

            except PermissionError:
                print(f"File locked, retrying... ({attempt+1}/10)")
                time.sleep(1)

            except Exception as e:
                print(f"Move failed: {e}")
                return

        print(f"Could not move {filename} (file still in use)")