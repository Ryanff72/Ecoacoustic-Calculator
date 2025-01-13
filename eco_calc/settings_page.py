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

		left_frame = tk.Frame(self)
		right_frame = tk.Frame(self)

		left_frame.grid(row=0, column=0, sticky="nsew")
		right_frame.grid(row=0, column=1, sticky="nsew")

		# Left Column title
		left_col_title = tk.Label(left_frame, text="Acoustic Index Selection", font=title_font)
		left_col_title.grid(row=0, column=0, padx=10, pady=(35, 5), sticky="nsew")

		# Right Column title
		right_col_title = tk.Label(right_frame, text="Calculation Settings", font=title_font)
		right_col_title.grid(row=0, column=1, padx=10, pady=(35, 5), sticky="nsew")

        # Calculate Index Button
		calculate_index_button = tk.Button(left_frame, text=f"Calculate", command=lambda: 
												AcousticTools.calculate_acoustic_index(DirectoryOperations.target_audio_folder,
													index_name=acoustic_index_dropdown.get(), 
													resolution_ms=int(float(resolution_entry_box.get()) * 1000), 
													batch_size_in_file_count=int(batch_size_entry_box.get()), 
													fft_window_size=int(fft_window_size_entry_box.get()), 
													hop_length=int(hop_length_entry_box.get()),
													num_bands=int(num_bands_entry_box.get())),
													font=button_font)
		calculate_index_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Calculate Index Dropdown
		indices = ["ACI", "ADI", "H","AEve", "M", "NDSI", "Bio"]
		acoustic_index_dropdown = ttk.Combobox(left_frame, values=indices, font=label_font)
		acoustic_index_dropdown.grid(row=1, column=0, padx=10, pady=10)	
		acoustic_index_dropdown.bind("<<ComboboxSelected>>", lambda event: SettingsPage.update_calculate_button(event, calculate_index_button, acoustic_index_dropdown.get()))

		# Resolution size in seconds box
		# This number is the length of the audio that you want to analyze
		resolution_box_label = tk.Label(right_frame, text="Data Resolution (How long do you want the analyzed clips to be, in seconds)", font=label_font)
		resolution_box_label.grid(row=1, column = 1, padx=10, pady=0, sticky="nsw")
		resolution_entry_box = tk.Entry(right_frame, width=10, font=label_font)
		resolution_entry_box.grid(row=2, column = 1, padx=10, pady=0, sticky="ns")
		resolution_entry_box.insert(0, "60")

		# Batch Size in file count
		batch_size_box_label = tk.Label(right_frame, text="Batch Size (Number of audio files loaded into memory at a time)", font=label_font)
		batch_size_box_label.grid(row=3, column = 1, padx=10, pady=0, sticky="nsw")
		batch_size_entry_box = tk.Entry(right_frame, width=10, font=label_font)
		batch_size_entry_box.grid(row=4, column = 1, padx=10, pady=0, sticky="ns")
		batch_size_entry_box.insert(0, "1")

		# Batch Size in file count
		fft_window_size_label = tk.Label(right_frame, text="FFT Window Size (Length of the FFT window in samples)", font=label_font)
		fft_window_size_label.grid(row=5, column = 1, padx=10, pady=5, sticky="nsw")
		fft_window_size_entry_box = tk.Entry(right_frame, width=10, font=label_font)
		fft_window_size_entry_box.grid(row=6, column = 1, padx=10, pady=0, sticky="ns")
		fft_window_size_entry_box.insert(0, "1024")

		# Hop length in audio samples
		hop_length_label = tk.Label(right_frame, text="Hop Length (Number of audio samples between successive FFT windows)", font=label_font)
		hop_length_label.grid(row=7, column=1, padx=10, pady=5, sticky="nsw")
		hop_length_entry_box = tk.Entry(right_frame, width=10, font=label_font)
		hop_length_entry_box.grid(row=8, column=1, padx=10, pady=0, sticky="ns")
		hop_length_entry_box.insert(0, "512")

		# Number of Bands
		num_bands_label = tk.Label(right_frame, text="Number of Bands (Number of frequency bands for analysis)", font=label_font)
		num_bands_label.grid(row=9, column=1, padx=10, pady=5, sticky="nsw")
		num_bands_entry_box = tk.Entry(right_frame, width=10, font=label_font)
		num_bands_entry_box.grid(row=10, column=1, padx=10, pady=0, sticky="ns")
		num_bands_entry_box.insert(0, "10")

	def update_calculate_button(event, button, index):
		button.config(text=f"Calculate {index}")