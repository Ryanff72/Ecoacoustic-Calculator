from tkinter import filedialog
class DirectoryOperations:
    def open_folder(): 
        file_path = filedialog.askdirectory(title="Select a File")
        if file_path:
            print(f"User selected: {file_path}")
            target_audio_folder = file_path
            eco_calc.x()