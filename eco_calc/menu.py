import ctypes
import glob
import tkinter as tk
import platform
from directory_operations import DirectoryOperations
from acoustic_tools import AcousticTools

class Menu:
    def create_main_menu():
        # Create a Window
        root = tk.Tk()
        root.title("Ecoacoustic_Calculator")
        root.geometry("640x480")

        # File Import Button
        file_import_button = tk.Button(root, text="File", command=DirectoryOperations.open_folder)
        file_import_button.pack(pady=50)
        file_import_button.place(x=5,y=5)

        # Calculate ACI Button
        calculate_aci_button = tk.Button(root, text="ACI", command=lambda: AcousticTools.find_aci(DirectoryOperations.target_audio_folder))
        calculate_aci_button.pack(pady=50)
        calculate_aci_button.place(x=5,y=50)

        # Event Loop
        root.mainloop()