import ctypes
from ctypes import c_char_p
from tkinter import filedialog
import glob
import os
eco_calc = ctypes.CDLL("./eco_calc.dll")

class AcousticTools:
    def find_aci(folder): 
        print(f"folder: {folder}")
        if folder:
            print(f"User selected: {folder}")
            target_audio_files = glob.glob(f"{folder}/*")
            for file in target_audio_files:
                eco_calc.aci(file.encode('utf-8'))