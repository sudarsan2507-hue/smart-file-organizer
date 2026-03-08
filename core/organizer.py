import os
import shutil


class FileOrganizer:

    def __init__(self, base_directory):

        self.base_directory = base_directory

        self.category_folders = {
            "Resume": "Resume",
            "Finance": "Finance",
            "Study": "Study",
            "Projects": "Projects",
            "Personal": "Personal",
            "Others": "Others"
        }


    def organize(self, file_path, category):

        folder_name = self.category_folders.get(category, "Others")

        destination_folder = os.path.join(self.base_directory, folder_name)

        # create folder if it doesn't exist
        os.makedirs(destination_folder, exist_ok=True)

        file_name = os.path.basename(file_path)

        destination_path = os.path.join(destination_folder, file_name)

        # move file
        shutil.move(file_path, destination_path)

        print(f"Moved {file_name} → {folder_name}")