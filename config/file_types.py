import os

def get_file_category(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    documents = [".pdf", ".docx", ".txt"]
    images = [".jpg", ".jpeg", ".png", ".gif"]
    videos = [".mp4", ".mkv", ".avi"]
    audio = [".mp3", ".wav"]
    archives = [".zip", ".rar"]

    if extension in documents:
        return "Documents"

    elif extension in images:
        return "Images"

    elif extension in videos:
        return "Videos"

    elif extension in audio:
        return "Audio"

    elif extension in archives:
        return "Archives"

    else:
        return "Others"