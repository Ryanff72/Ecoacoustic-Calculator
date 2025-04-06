import ctypes
import glob
import tkinter as tk
from tkinter import ttk
import platform
from directory_operations import DirectoryOperations
from acoustic_tools import AcousticTools
from graph_page import GraphPage
from errorbar import Errorbar
from instance_manager import InstanceManager

class SettingsPage(tk.Frame):
	def __init__(self, parent, controller, title_font, label_font, button_font):
		super().__init__(parent)

		self.grid(sticky="nsew")

		self.acoustic_index_result = None

		self.AID_source = "(https://besjournals.onlinelibrary.wiley.com /doi/full/10.1111/2041-210X.13254)"

		self.acoustic_index_descriptions = {
			"ACI": """Acoustic Complexity Index (ACI). Based on difference in amplitude between one time sample and the next within a frequency band, relative to the total amplitude within that band. Designed to quantify the inherent irregularity in biophony, while being relatively impervious to persistent sound of a constant intensity. High values indicate storms, intermittent rain drops falling from vegetation, stridulating insects, or high levels of bird activity. Lowest values came from recordings with consistent cicada noise that fills the whole spectrogram.\n"""
			+ self.AID_source,
			"ADI": """Acoustic Diversity Index (ADI). Increases with greater evenness across frequency bands. An even signal (either noisy across all frequency bands or completely silent) will give a high value, whereas a pure tone (i.e. all energy in one frequency band) will be closer to 0.  Highest values were from recordings with high levels of geophony or anthrophony (wind, helicopters or trucks) blanketing the spectrogram with noise, or from very quiet recordings with little variation among frequency bands.  Lowest values reflect dominance of a narrow frequency band, usually by nocturnal insect noise.\n""" 
			+ self.AID_source, 
			"H": """Acoustic Entropy (H). Measures the randomness of the sound energy distribution across frequency bands. Highest values come from near-silent recordings, with no wind, and only faint bird calls. Lowest values produced when insect noise dominated a single frequency band.\n""" 
			+ self.AID_source,
			"AEve": """Acoustic Evenness (AEve). Measures the evenness of the sound energy distribution across frequency bands. Reverse of ADI patterns. High values identify recordings with dominance by a narrow frequency band of insect noise. Low values are associated with windy recordings with many occupied frequency bands, or near silent recordings with no acoustic activity.\n""" 
				+ self.AID_source,
			"M": """Acoustic Complexity Index (M). Measures the number of peaks in the spectrogram, which is related to the number of sound sources. Highest values associated with high levels of geophony, particularly storms. Low levels of M produced by very quiet recordings, with little biophony or geophony.\n""" 
				+ self.AID_source,
			"NDSI": """Normalized Difference Soundscape Index (NDSI). Measures the difference between the day and night soundscape. High values reflect high levels of insect biophony, with minimal noise in the 1–2 kHz range. Low values arise when insect biophony dominates the 1–2 kHz band.\n""" 
				+ self.AID_source,
			"Bio": """Bioacoustic Index (Bio). Measures the number of peaks in the spectrogram, which is related to the number of sound sources. Highest values produced by blanket cicada noise, with high amplitude and minimal variation among frequency bands. Low values arise when there is no sound between 2 and 11 kHz, although there is sometimes insect biophony outside these bounds.\n""" 
			+ self.AID_source
		}

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

        # Calculate Index Dropdown
		indices = ["ACI", "ADI", "H","AEve", "M", "NDSI", "Bio"]
		self.acoustic_index_dropdown = ttk.Combobox(left_frame, values=indices, font=label_font)
		self.acoustic_index_dropdown.set("ACI")
		self.acoustic_index_dropdown.grid(row=1, column=0, padx=10, pady=10)	
		self.acoustic_index_dropdown.bind("<<ComboboxSelected>>", lambda event: SettingsPage.update_calculate_button(event, calculate_index_button, self.acoustic_index_dropdown.get()))

		# Resolution size in seconds box
		# This number is the length of the audio that you want to analyze
		resolution_box_label = tk.Label(right_frame, text="Data Resolution (How long do you want the analyzed clips to be, in seconds)", font=label_font)
		resolution_box_label.grid(row=1, column = 1, padx=10, pady=0, sticky="nsw")
		self.resolution_entry_box = tk.Entry(right_frame, width=10, font=label_font)
		self.resolution_entry_box.grid(row=2, column = 1, padx=10, pady=0, sticky="ns")
		self.resolution_entry_box.insert(0, "60")

		# Batch Size in file count
		batch_size_box_label = tk.Label(right_frame, text="Batch Size (Number of audio files loaded into memory at a time)", font=label_font)
		batch_size_box_label.grid(row=3, column = 1, padx=10, pady=0, sticky="nsw")
		self.batch_size_entry_box = tk.Entry(right_frame, width=10, font=label_font)
		self.batch_size_entry_box.grid(row=4, column = 1, padx=10, pady=0, sticky="ns")
		self.batch_size_entry_box.insert(0, "1")

		# Batch Size in file count
		fft_window_size_label = tk.Label(right_frame, text="FFT Window Size (Length of the FFT window in samples)", font=label_font)
		fft_window_size_label.grid(row=5, column = 1, padx=10, pady=5, sticky="nsw")
		self.fft_window_size_entry_box = tk.Entry(right_frame, width=10, font=label_font)
		self.fft_window_size_entry_box.grid(row=6, column = 1, padx=10, pady=0, sticky="ns")
		self.fft_window_size_entry_box.insert(0, "1024")

		# Hop length in audio samples
		hop_length_label = tk.Label(right_frame, text="Hop Length (Number of audio samples between successive FFT windows)", font=label_font)
		hop_length_label.grid(row=7, column=1, padx=10, pady=5, sticky="nsw")
		self.hop_length_entry_box = tk.Entry(right_frame, width=10, font=label_font)
		self.hop_length_entry_box.grid(row=8, column=1, padx=10, pady=0, sticky="ns")
		self.hop_length_entry_box.insert(0, "512")

		# Number of Bands
		num_bands_label = tk.Label(right_frame, text="Number of Bands (Number of frequency bands for analysis)", font=label_font)
		num_bands_label.grid(row=9, column=1, padx=10, pady=5, sticky="nsw")
		self.num_bands_entry_box = tk.Entry(right_frame, width=10, font=label_font)
		self.num_bands_entry_box.grid(row=10, column=1, padx=10, pady=0, sticky="ns")
		self.num_bands_entry_box.insert(0, "10")

		# Bin Step
		bin_step_label = tk.Label(right_frame, text="Bin Step (Number of bins when dividing the audio spectrum into frequency bands)", font=label_font)
		bin_step_label.grid(row=9, column=1, padx=10, pady=5, sticky="nsw")
		self.bin_step_entry_box = tk.Entry(right_frame, width=10, font=label_font)
		self.bin_step_entry_box.grid(row=10, column=1, padx=10, pady=0, sticky="ns")
		self.bin_step_entry_box.insert(0, "10")

		# Frequency Range (Hz) Label
		freq_range_label = tk.Label(right_frame, text="Frequency Range (Hz, min - max) (Frequencies outside this range will not be considered)", font=label_font)
		freq_range_label.grid(row=13, column=1, padx=10, pady=5, sticky="nsw")

		# Nested Frame for Entry Boxes
		freq_frame = tk.Frame(right_frame)
		freq_frame.grid(row=14, column=1, padx=10, pady=0, sticky="n")

		# Min Frequency Entry
		self.min_freq_entry_box = tk.Entry(freq_frame, width=10, font=label_font)
		self.min_freq_entry_box.pack(side=tk.LEFT, padx=(0, 5))  # Left side, small gap to right
		self.min_freq_entry_box.insert(0, "20")

		# Max Frequency Entry (side by side with min)
		self.max_freq_entry_box = tk.Entry(freq_frame, width=10, font=label_font)
		self.max_freq_entry_box.pack(side=tk.LEFT, padx=(5, 0))  # Left side, small gap to left
		self.max_freq_entry_box.insert(0, "20000")

		# Biophony Range (Hz) Label
		bio_range_label = tk.Label(right_frame, text="Biophony Range (Hz, min-max) (Frequency range for biological sounds)", font=label_font)
		bio_range_label.grid(row=15, column=1, padx=10, pady=5, sticky="nsw")

		# Nested Frame for Entry Boxes
		bio_frame = tk.Frame(right_frame)
		bio_frame.grid(row=16, column=1, padx=10, pady=0, sticky="n")

		# Min Frequency Entry
		self.min_bio_entry_box = tk.Entry(bio_frame, width=10, font=label_font)
		self.min_bio_entry_box.pack(side=tk.LEFT, padx=(0, 5))  # Left side, small gap to right
		self.min_bio_entry_box.insert(0, "20")

		# Max Frequency Entry (side by side with min)
		self.max_bio_entry_box = tk.Entry(bio_frame, width=10, font=label_font)
		self.max_bio_entry_box.pack(side=tk.LEFT, padx=(5, 0))  # Left side, small gap to left
		self.max_bio_entry_box.insert(0, "20000")

		# Anthrophony Range (Hz) Label
		anthro_range_label = tk.Label(right_frame, text="Anthrophony Range (Hz, min-max) (Frequency range for human-made sounds)", font=label_font)
		anthro_range_label.grid(row=17, column=1, padx=10, pady=5, sticky="nsw")

		# Nested Frame for Entry Boxes
		anthro_frame = tk.Frame(right_frame)
		anthro_frame.grid(row=18, column=1, padx=10, pady=0, sticky="n")

		# Min Frequency Entry
		self.min_anthro_entry_box = tk.Entry(anthro_frame, width=10, font=label_font)
		self.min_anthro_entry_box.pack(side=tk.LEFT, padx=(0, 5))  # Left side, small gap to right
		self.min_anthro_entry_box.insert(0, "20")

		# Max Frequency Entry (side by side with min)
		self.max_anthro_entry_box = tk.Entry(anthro_frame, width=10, font=label_font)
		self.max_anthro_entry_box.pack(side=tk.LEFT, padx=(5, 0))  # Left side, small gap to left
		self.max_anthro_entry_box.insert(0, "20000")

		# Acoustic Index Description Label
		self.acoustic_index_description_label = tk.Label(left_frame, text=self.acoustic_index_descriptions.get(self.acoustic_index_dropdown.get()), font=label_font, wraplength=350, justify="left")
		self.acoustic_index_description_label.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        # Calculate Index Button
		calculate_index_button = tk.Button(left_frame, text=f"Calculate", command=self.calculate_index, font=button_font)
		calculate_index_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
	
	def calculate_index(self):
		try:
			self.acoustic_index_result = AcousticTools.calculate_acoustic_index(
				DirectoryOperations.target_audio_folder,
				index_name=self.acoustic_index_dropdown.get(), 
				resolution_ms=int(float(self.resolution_entry_box.get()) * 1000), 
				batch_size_in_file_count=int(self.batch_size_entry_box.get()), 
				fft_window_size=int(self.fft_window_size_entry_box.get()), 
				hop_length=int(self.hop_length_entry_box.get()),
				bin_step=int(self.bin_step_entry_box.get()),
				min_freq=int(self.min_freq_entry_box.get()),
				max_freq=int(self.max_freq_entry_box.get()),
				min_bio=int(self.min_bio_entry_box.get()),
				max_bio=int(self.max_bio_entry_box.get()),
				min_anthro=int(self.min_anthro_entry_box.get()),
				max_anthro=int(self.max_anthro_entry_box.get())
			)
			InstanceManager.get_instance("GraphPage").create_graph(self.acoustic_index_dropdown.get(), self.acoustic_index_result)
		except IsADirectoryError as e:
			InstanceManager.get_instance(Errorbar.__name__).update_text(text=f"Please select a folder using 'File': {e}")
			print(e)
		except PermissionError as e:
			InstanceManager.get_instance(Errorbar.__name__).update_text(text=f"Permission error. Select a different file 'File': {e}")
			print(e)
		#except Exception as e:
		#	InstanceManager.get_instance(Errorbar.__name__).update_text(text=f"Unknown Error: {e}")
		#	print(e)

	def update_calculate_button(event, button, index):
		button.config(text=f"Calculate {index}")
		InstanceManager.get_instance(SettingsPage.__name__).acoustic_index_description_label.config(text=InstanceManager.get_instance("SettingsPage").acoustic_index_descriptions.get(index))
