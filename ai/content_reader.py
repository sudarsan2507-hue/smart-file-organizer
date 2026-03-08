import os
import fitz #for_pdfs
import docx
import pandas as pd


class ContentReader:

    def read_file(self, file_path):
        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".txt":
            return self.read_txt(file_path)

        elif extension == ".pdf":
            return self.read_pdf(file_path)

        elif extension == ".docx":
            return self.read_docx(file_path)

        elif extension == ".xlsx":
            return self.read_excel(file_path)

        elif extension == ".csv":
            return self.read_csv(file_path)

        else:
            return ""


    def read_txt(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except:
            return ""


    def read_pdf(self, file_path):
        text = ""

        try:
            document = fitz.open(file_path)

            for page in document:
                text += page.get_text()

            return text

        except:
            return ""


    def read_docx(self, file_path):
        text = ""

        try:
            document = docx.Document(file_path)

            for paragraph in document.paragraphs:
                text += paragraph.text + " "

            return text

        except:
            return ""


    def read_excel(self, file_path):
        text = ""

        try:
            data = pd.read_excel(file_path)

            for column in data.columns:
                text += column + " "

            for row in data.values:
                for cell in row:
                    text += str(cell) + " "

            return text

        except:
            return ""


    def read_csv(self, file_path):
        text = ""

        try:
            data = pd.read_csv(file_path)

            for column in data.columns:
                text += column + " "

            for row in data.values:
                for cell in row:
                    text += str(cell) + " "

            return text

        except:
            return ""