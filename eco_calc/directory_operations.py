from tkinter import filedialog

class DirectoryOperations:
    target_audio_folder = ""

    @staticmethod
    def open_folder(): 
        file_path = filedialog.askdirectory(title="Select a File")
        if file_path:
            print(f"User selected: {file_path}")
            DirectoryOperations.target_audio_folder = file_path