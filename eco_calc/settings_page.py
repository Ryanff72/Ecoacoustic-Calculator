import ctypes
import glob
import tkinter as tk
from tkinter import ttk
import platform
from directory_operations import DirectoryOperations
from acoustic_tools import AcousticTools

class SettingsPage(tk.Frame):
	def __init__(self, parent, controller, title_font, label_font, button_font):
		super().__init__(parent)

		self.grid(sticky="nsew")

		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		self.grid_rowconfigure(2, weight=1)

		# Left Column title
		left_col_title = tk.Label(self, text="Acoustic Index Selection", font=title_font)
		left_col_title.grid(row=0, column=0, padx=10, pady=(35, 5), sticky="nsew")

		# Right Column title
		right_col_title = tk.Label(self, text="Calculation Settings", font=title_font)
		right_col_title.grid(row=0, column=1, padx=10, pady=(35, 5), sticky="nsew")

        # Calculate Index Button
		calculate_index_button = tk.Button(self, text=f"Calculate", command=lambda: AcousticTools.calculate_acoustic_index(DirectoryOperations.target_audio_folder, acoustic_index_dropdown.get(), resolution_ms=int(float(resolution_entry_box.get()) * 1000), batch_size_in_file_count=int(batch_size_entry_box.get())), font=button_font)
		calculate_index_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Calculate Index Dropdown
		indices = ["ACI", "ADI", "H","AEve", "M", "NDSI", "Bio"]
		acoustic_index_dropdown = ttk.Combobox(self, values=indices, font=label_font)
		acoustic_index_dropdown.grid(row=1, column=0, padx=10, pady=10)	
		acoustic_index_dropdown.bind("<<ComboboxSelected>>", lambda event: SettingsPage.update_calculate_button(event, calculate_index_button, acoustic_index_dropdown.get()))

		# Resolution size in seconds box
		# This number is the length of the audio that you want to analyze
		resolution_box_label = tk.Label(self, text="Data Resolution (How long do you want the analyzed clips to be, in seconds)", font=label_font)
		resolution_box_label.grid(row=1, column = 1, padx=10, pady=5, sticky="w")
		resolution_entry_box = tk.Entry(self, width=10, font=label_font)
		resolution_entry_box.grid(row=2, column = 1, padx=10, pady=0, sticky="n")

		# Batch Size in file count
		batch_size_box_label = tk.Label(self, text="Batch Size (Number of audio files loaded into memory at a time)", font=label_font)
		batch_size_box_label.grid(row=3, column = 1, padx=10, pady=5, sticky="w")
		batch_size_entry_box = tk.Entry(self, width=10, font=label_font)
		batch_size_entry_box.grid(row=4, column = 1, padx=10, pady=0, sticky="n")

	def update_calculate_button(event, button, index):
		button.config(text=f"Calculate {index}")