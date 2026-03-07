import os
import shutil

def move_file(file_path, category):

    base_folder = os.path.dirname(file_path)
    target_folder = os.path.join(base_folder, category)

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    file_name = os.path.basename(file_path)
    destination = os.path.join(target_folder, file_name)

    shutil.move(file_path, destination)

    print(f"File moved to: {destination}")