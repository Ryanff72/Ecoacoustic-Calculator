from tkinter import filedialog
import glob
import os

class AcousticTools:
    def find_aci(): 
        file_path = filedialog.askdirectory(title="Select a File")
        if file_path:
            print(f"User selected: {file_path}")
            target_audio_files = glob.glob(file_path)
            for file in target_audio_files:
                eco_calc.aci(file)