import ctypes
import glob
import tkinter as tk
from tkinter import ttk
import platform
from directory_operations import DirectoryOperations
from acoustic_tools import AcousticTools

class Menu:
	def create_main_menu():
		root = tk.Tk()
		root.title("Ecoacoustic_Calculator")
		root.geometry("640x480")
		# Create a Window
		# File Import Button
		file_import_button = tk.Button(root, text="File", command=DirectoryOperations.open_folder)
		file_import_button.pack(pady=50)
		file_import_button.place(x=5,y=5)

		calculate_index_button = tk.Button(root, text=f"Calculate", command=lambda: AcousticTools.calculate_acoustic_index(DirectoryOperations.target_audio_folder, acoustic_index_dropdown.get()))
		calculate_index_button.pack(pady=50)
		calculate_index_button.place(x=5,y=50)
        # Calculate Index Dropdown

		indices = ["ACI", "ADI", "H","AEve", "M", "NDSI", "Bio"]
		acoustic_index_dropdown = ttk.Combobox(root, values=indices)
		acoustic_index_dropdown.pack()	
		acoustic_index_dropdown.bind("<<ComboboxSelected>>", lambda event: Menu.update_calculate_button(event, calculate_index_button, acoustic_index_dropdown.get()))
        # Calculate Index Button

		# Event Loop
		root.mainloop()

	def update_calculate_button(event, button, index):
		button.config(text=f"Calculate {index}")
